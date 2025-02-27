from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from models import User, PasswordResetToken, Device, AuditLog
import secrets
import logging
import pyotp
from ratelimit import limits, sleep_and_retry
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configurations
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(64))  # Generate a secure key if not set
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
PASSWORD_RESET_EXPIRE_HOURS = 24
MAX_LOGIN_ATTEMPTS = 5
MAX_REQUESTS_PER_MINUTE = 60

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Rate limiting decorator
@sleep_and_retry
@limits(calls=MAX_REQUESTS_PER_MINUTE, period=60)
def rate_limit():
    """Rate limiting utility function"""
    pass

def get_password_hash(password: str) -> str:
    """Generate a secure password hash using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Create a new JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "refresh": True})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def authenticate_user(username: str, password: str, db: AsyncSession) -> Optional[User]:
    """Authenticate a user and update login attempts"""
    try:
        rate_limit()
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        
        if not user or not verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt for username: {username}")
            return None
            
        # Reset login attempts on successful login
        user.last_login = datetime.utcnow()
        await db.commit()
        
        return user
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication error")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """Get the current authenticated user from JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive")
        
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Verify the current user has admin privileges"""
    if current_user.role != "admin":
        logger.warning(f"Unauthorized admin access attempt by user: {current_user.username}")
        raise HTTPException(status_code=403, detail="Operation not permitted")
    return current_user

def generate_reset_token() -> str:
    """Generate a secure password reset token"""
    return secrets.token_urlsafe(32)

async def is_token_valid(token: str, db: AsyncSession) -> Optional[PasswordResetToken]:
    """Verify if a password reset token is valid and not expired"""
    result = await db.execute(select(PasswordResetToken).where(
        PasswordResetToken.token == token,
        PasswordResetToken.is_used == False
    ))
    reset_token = result.scalars().first()
    
    if reset_token and reset_token.expires_at > datetime.utcnow():
        return reset_token
    return None

async def verify_device_token(device_id: int, token: str, db: AsyncSession) -> Device:
    """Verify a device's authentication token"""
    result = await db.execute(select(Device).where(
        Device.id == device_id,
        Device.token == token
    ))
    device = result.scalars().first()
    
    if not device:
        logger.warning(f"Invalid device token attempt for device ID: {device_id}")
        raise HTTPException(status_code=403, detail="Invalid device token")
    
    # Update device last seen timestamp
    device.last_seen = datetime.utcnow()
    await db.commit()
    
    return device

def generate_mfa_secret() -> str:
    """Generate a new MFA secret key"""
    return pyotp.random_base32()

def verify_mfa_token(secret: str, token: str) -> bool:
    """Verify a MFA token against the secret"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token)

async def log_security_event(db: AsyncSession, user_id: int, action: str, details: str, ip_address: Optional[str] = None) -> None:
    """Log security-related events to the audit log"""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=ip_address
    )
    db.add(audit_log)
    await db.commit()

def validate_password_strength(password: str) -> bool:
    """Validate password meets minimum security requirements"""
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in '!@#$%^&*()' for c in password):
        return False
    return True