from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "standard"

class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[str]

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    mfa_enabled: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class DeviceCreate(BaseModel):
    name: str
    user_id: int

class DeviceUpdate(BaseModel):
    name: Optional[str]
    status: Optional[str]

class DeviceOut(BaseModel):
    id: int
    name: str
    user_id: int
    token: str
    status: str
    last_seen: Optional[datetime]

    class Config:
        orm_mode = True

class CommandRequest(BaseModel):
    command: str

class CommandLogOut(BaseModel):
    id: int
    device_id: int
    command: str
    output: Optional[str]
    timestamp: datetime
    status: str

    class Config:
        orm_mode = True

class AuditLogOut(BaseModel):
    id: int
    user_id: int
    action: str
    details: Optional[str]
    timestamp: datetime

    class Config:
        orm_mode = True

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class FileOperation(BaseModel):
    operation: str
    filename: str
    content: Optional[str]
    new_filename: Optional[str]

class ProcessRequest(BaseModel):
    action: str
    process_name: Optional[str]

class ClipboardRequest(BaseModel):
    action: str
    content: Optional[str]