from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta
from models import User, PasswordResetToken
from schemas import UserCreate, UserOut, Token, UserUpdate, PasswordResetRequest, PasswordResetConfirm
from utils import (
    get_password_hash, create_access_token, create_refresh_token, authenticate_user,
    get_current_user, generate_reset_token, is_token_valid, validate_password_strength,
    verify_mfa_token, generate_mfa_secret, log_security_event, rate_limit
)
from database import get_db
import qrcode
import io
import base64

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=UserOut)
@rate_limit
async def register_user(user: UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    # Validate password strength
    if not validate_password_strength(user.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long and contain uppercase, lowercase, numbers, and special characters"
        )

    # Check for existing username or email
    result = await db.execute(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username or email already registered")

    # Create new user
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role or "user",
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Log the registration event
    await log_security_event(
        db=db,
        user_id=new_user.id,
        action="REGISTER",
        details=f"New user registration: {user.username}",
        ip_address=request.client.host
    )
    
    return new_user

@router.post("/token", response_model=Token)
@rate_limit
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required"
        )

    try:
        user = await authenticate_user(form_data.username, form_data.password, db)
        if not user:
            await log_security_event(
                db=db,
                user_id=0,  # 0 indicates failed login attempt
                action="LOGIN_FAILED",
                details=f"Failed login attempt for username: {form_data.username}",
                ip_address=request.client.host
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if MFA is required
        mfa_token = getattr(form_data, 'mfa_token', None)
        if user.mfa_enabled and not mfa_token:
            return {"requires_mfa": True, "message": "MFA token required"}
        
        if user.mfa_enabled:
            if not verify_mfa_token(user.mfa_secret, mfa_token):
                await log_security_event(
                    db=db,
                    user_id=user.id,
                    action="MFA_FAILED",
                    details="Invalid MFA token provided",
                    ip_address=request.client.host
                )
                raise HTTPException(status_code=401, detail="Invalid MFA token")

        # Generate tokens
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})
        
        # Log successful login
        await log_security_event(
            db=db,
            user_id=user.id,
            action="LOGIN",
            details="Successful login",
            ip_address=request.client.host
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        await log_security_event(
            db=db,
            user_id=0,
            action="LOGIN_ERROR",
            details=f"Unexpected error during login: {str(e)}",
            ip_address=request.client.host
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )

@router.post("/refresh")
@rate_limit
async def refresh_token(request: Request, current_user: User = Depends(get_current_user)):
    new_access_token = create_access_token(data={"sub": current_user.username})
    await log_security_event(
        db=request.state.db,
        user_id=current_user.id,
        action="TOKEN_REFRESH",
        details="Access token refreshed",
        ip_address=request.client.host
    )
    return {"access_token": new_access_token, "token_type": "bearer"}

@router.put("/profile", response_model=UserOut)
@rate_limit
async def update_profile(
    request: Request,
    update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if update.username and update.username != current_user.username:
        result = await db.execute(select(User).where(User.username == update.username))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = update.username

    if update.email and update.email != current_user.email:
        result = await db.execute(select(User).where(User.email == update.email))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = update.email

    await db.commit()
    await db.refresh(current_user)
    
    await log_security_event(
        db=db,
        user_id=current_user.id,
        action="PROFILE_UPDATE",
        details="User profile updated",
        ip_address=request.client.host
    )
    
    return current_user

@router.post("/mfa/enable")
@rate_limit
async def enable_mfa(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA is already enabled")

    # Generate new MFA secret
    secret = generate_mfa_secret()
    current_user.mfa_secret = secret
    current_user.mfa_enabled = True
    
    # Generate QR code
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        current_user.email,
        issuer_name="Fatakeshto Application"
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img_buffer = io.BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(img_buffer)
    qr_code = base64.b64encode(img_buffer.getvalue()).decode()
    
    await db.commit()
    
    await log_security_event(
        db=db,
        user_id=current_user.id,
        action="MFA_ENABLED",
        details="MFA enabled for user",
        ip_address=request.client.host
    )
    
    return {
        "secret": secret,
        "qr_code": f"data:image/png;base64,{qr_code}"
    }

@router.post("/password-reset/request")
@rate_limit
async def request_password_reset(request: Request, reset_request: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == reset_request.email))
    user = result.scalars().first()
    
    if user:
        # Delete any existing reset tokens for this user
        await db.execute(
            select(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
        )
        
        token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        
        db.add(reset_token)
        await db.commit()
        
        # TODO: Implement email sending here
        # For development, just print the token
        print(f"Reset token for {user.email}: {token}")
        
        await log_security_event(
            db=db,
            user_id=user.id,
            action="PASSWORD_RESET_REQUEST",
            details="Password reset requested",
            ip_address=request.client.host
        )
    
    # Always return the same message to prevent user enumeration
    return {"message": "If the email exists, a reset link has been sent."}

@router.post("/password-reset/confirm")
@rate_limit
async def confirm_password_reset(
    request: Request,
    confirm: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    if not validate_password_strength(confirm.new_password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long and contain uppercase, lowercase, numbers, and special characters"
        )

    reset_token = await is_token_valid(confirm.token, db)
    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    result = await db.execute(select(User).where(User.id == reset_token.user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Update password and mark token as used
    user.hashed_password = get_password_hash(confirm.new_password)
    reset_token.is_used = True