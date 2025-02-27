from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime, timedelta
from ..database import get_db
from ..models import User, Device, AuditLog
from ..schemas import UserCreate, UserUpdate, DeviceCreate, DeviceUpdate, AuditLogResponse
from ..utils import get_current_admin_user, get_password_hash
import csv
from fastapi.responses import StreamingResponse
from io import StringIO

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=List[User])
async def list_users(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_admin_user),
                    db: AsyncSession = Depends(get_db)):
    """List all users in the system"""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, current_user: User = Depends(get_current_admin_user),
                     db: AsyncSession = Depends(get_db)):
    """Create a new user"""
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role=user.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate,
                     current_user: User = Depends(get_current_admin_user),
                     db: AsyncSession = Depends(get_db)):
    """Update user details"""
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user.dict(exclude_unset=True).items():
        if field == "password":
            setattr(db_user, "hashed_password", get_password_hash(value))
        else:
            setattr(db_user, field, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current_user: User = Depends(get_current_admin_user),
                     db: AsyncSession = Depends(get_db)):
    """Delete a user"""
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(db_user)
    await db.commit()

@router.get("/devices", response_model=List[Device])
async def list_devices(skip: int = 0, limit: int = 100,
                      current_user: User = Depends(get_current_admin_user),
                      db: AsyncSession = Depends(get_db)):
    """List all devices in the system"""
    result = await db.execute(select(Device).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(skip: int = 0, limit: int = 100,
                        current_user: User = Depends(get_current_admin_user),
                        db: AsyncSession = Depends(get_db)):
    """Get system audit logs"""
    result = await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/reports/audit-logs/csv")
async def download_audit_logs_report(days: int = 30,
                                   current_user: User = Depends(get_current_admin_user),
                                   db: AsyncSession = Depends(get_db)):
    """Generate and download audit logs report in CSV format"""
    start_date = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.timestamp >= start_date)
        .order_by(AuditLog.timestamp.desc())
    )
    logs = result.scalars().all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "User ID", "Action", "Details", "IP Address"])
    
    for log in logs:
        writer.writerow([
            log.timestamp.isoformat(),
            log.user_id,
            log.action,
            log.details,
            log.ip_address or "N/A"
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=audit_logs_{datetime.utcnow().date()}.csv"}
    )