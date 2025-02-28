from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums for consistent value validation
class UserRole(str, Enum):
    ADMIN = "admin"
    STANDARD = "standard"
    READ_ONLY = "read_only"

class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    SUSPENDED = "suspended"

class CommandStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class FileOperationType(str, Enum):
    UPLOAD = "upload"
    DOWNLOAD = "download"
    DELETE = "delete"
    RENAME = "rename"

class ProcessAction(str, Enum):
    START = "start"
    STOP = "stop"
    LIST = "list"

class ClipboardAction(str, Enum):
    GET = "get"
    SET = "set"

# Base Models
class TimestampModel(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = Field(default=UserRole.STANDARD)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    mfa_enabled: Optional[bool] = None

class UserOut(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    mfa_enabled: bool

    class Config:
        from_attributes = True

class User(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    mfa_enabled: bool

    class Config:
        from_attributes = True

# Device schemas
class DeviceBase(BaseModel):
    name: str
    device_id: str

class DeviceCreate(DeviceBase):
    owner_id: int

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    is_online: Optional[bool] = None
    ip_address: Optional[str] = None
    os_info: Optional[str] = None

class Device(DeviceBase):
    id: int
    owner_id: int
    is_online: bool
    last_seen: Optional[datetime]
    created_at: datetime
    ip_address: Optional[str]
    os_info: Optional[str]

    class Config:
        from_attributes = True

# Log schemas
class DeviceLogBase(BaseModel):
    command: str
    device_id: int

class DeviceLogCreate(DeviceLogBase):
    pass

class DeviceLog(DeviceLogBase):
    id: int
    output: Optional[str]
    executed_at: datetime
    status: str

    class Config:
        from_attributes = True

class AuditLogBase(BaseModel):
    action: str
    details: str
    user_id: int

class AuditLogCreate(AuditLogBase):
    ip_address: Optional[str]

class AuditLog(AuditLogBase):
    id: int
    timestamp: datetime
    ip_address: Optional[str]

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None

# Password Reset schemas
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

# Command schemas
class CommandRequest(BaseModel):
    command: str
    args: Optional[List[str]] = None

    class Config:
        from_attributes = True

class CommandLogOut(BaseModel):
    id: Optional[int] = None
    device_id: int
    command: str
    output: str
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    status: CommandStatus = Field(default=CommandStatus.COMPLETED)

    class Config:
        from_attributes = True

class ProcessRequest(BaseModel):
    action: ProcessAction
    process_name: Optional[str] = None

    class Config:
        from_attributes = True

class ClipboardRequest(BaseModel):
    action: ClipboardAction
    content: Optional[str] = None

    class Config:
        from_attributes = True

class FileOperation(BaseModel):
    operation_type: FileOperationType
    file_path: str
    new_path: Optional[str] = None  # Used for rename operations
    content: Optional[str] = None   # Used for upload operations

    class Config:
        from_attributes = True