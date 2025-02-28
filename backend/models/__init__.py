from database import Base
from .error_log import ErrorLog
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STANDARD = "standard"
    READ_ONLY = "read_only"

class DeviceStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"

class CommandStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    EXECUTING = "executing"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.STANDARD)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_login = Column(DateTime(timezone=True), nullable=True)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)

    # Relationships
    devices = relationship("Device", back_populates="owner", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.OFFLINE)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    ip_address = Column(String(255), nullable=True)
    os_info = Column(String(255), nullable=True)

    # Relationships
    owner = relationship("User", back_populates="devices")
    command_logs = relationship("CommandLog", back_populates="device", cascade="all, delete-orphan")
    queued_commands = relationship("CommandQueue", back_populates="device", cascade="all, delete-orphan")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    details = Column(Text)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    ip_address = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    is_used = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="reset_tokens")

class CommandQueue(Base):
    __tablename__ = "command_queue"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    command = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    status = Column(Enum(CommandStatus), default=CommandStatus.PENDING)
    priority = Column(Integer, default=0)
    execute_after = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    device = relationship("Device", back_populates="queued_commands")

__all__ = ['Base', 'ErrorLog', 'User', 'UserRole', 'DeviceStatus', 'CommandStatus',
           'Device', 'AuditLog', 'PasswordResetToken', 'CommandQueue']