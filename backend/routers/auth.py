from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .database import get_db
from .models import User, PasswordResetToken
from .schemas import UserCreate, UserOut, Token, UserUpdate, PasswordResetRequest, PasswordResetConfirm
from .utils import get_password_hash, create_access_token, authenticate_user, get_current_user, generate_reset_token, is_token_valid
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if user.mfa_enabled:
        # Placeholder for MFA verification
        pass
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.put("/profile", response_model=UserOut)
async def update_profile(update: UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if update.username:
        current_user.username = update.username
    if update.email:
        current_user.email = update.email
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.post("/password-reset/request")
async def request_password_reset(request: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalars().first()
    if user:
        token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)
        reset_token = PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at)
        db.add(reset_token)
        await db.commit()
        # Placeholder for email sending
        print(f"Reset token for {user.email}: {token}")
    return {"message": "If the email exists, a reset link has been sent."}

@router.post("/password-reset/confirm")
async def confirm_password_reset(confirm: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    reset_token = await is_token_valid(confirm.token, db)
    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    result = await db.execute(select(User).where(User.id == reset_token.user_id))
    user = result.scalars().first()
    user.hashed_password = get_password_hash(confirm.new_password)
    await db.delete(reset_token)
    await db.commit()
    return {"message": "Password reset successfully"}