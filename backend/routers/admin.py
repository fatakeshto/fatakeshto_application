from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import User, Device, AuditLog
from schemas import UserCreate, UserOut, DeviceCreate, DeviceOut, DeviceUpdate, AuditLogOut
from utils import get_current_admin_user
import uuid
import logging

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)

@router.post("/users", response_model=UserOut)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    from .utils import get_password_hash
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = User(username=user.username, email=user.email, hashed_password=get_password_hash(user.password), role=user.role)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    audit_log = AuditLog(user_id=admin.id, action="create_user", details=f"Created user {new_user.id}")
    db.add(audit_log)
    await db.commit()
    logger.info(f"Admin {admin.username} created user {new_user.id}")
    return new_user

@router.get("/reports", response_model=list[AuditLogOut])
async def generate_report(format: str = Query("csv"), page: int = Query(1), limit: int = Query(10), db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    offset = (page - 1) * limit
    result = await db.execute(select(AuditLog).offset(offset).limit(limit))
    logs = result.scalars().all()
    logger.info(f"Admin {admin.username} generated {format} report, page {page}")
    return logs