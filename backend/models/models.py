from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STANDARD = "standard"
    READ_ONLY = "read_only"

class DeviceStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class CommandStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

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
    name = Column(String(255))
    device_type = Column(String(50))
    status = Column(Enum(DeviceStatus), default=DeviceStatus.OFFLINE)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String(255), unique=True)

    # Relationships
    owner = relationship("User", back_populates="devices")
    command_logs = relationship("CommandLog", back_populates="device", cascade="all, delete-orphan")
    command_queue = relationship("CommandQueue", back_populates="device", cascade="all, delete-orphan")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(255))
    details = Column(Text, nullable=True)
    ip_address = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String(255), unique=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True))
    is_used = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="reset_tokens")

class CommandLog(Base):
    __tablename__ = "command_logs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    command = Column(String(255))
    output = Column(Text, nullable=True)
    status = Column(Enum(CommandStatus), default=CommandStatus.PENDING)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    device = relationship("Device", back_populates="command_logs")

class CommandQueue(Base):
    __tablename__ = "command_queue"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    command = Column(String(255))
    status = Column(Enum(CommandStatus), default=CommandStatus.PENDING)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    execute_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    device = relationship("Device", back_populates="command_queue")