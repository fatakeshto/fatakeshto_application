from fastapi import APIRouter, Depends, HTTPException, WebSocket, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from typing import List

from database import get_db
from models import Device, CommandLog, CommandQueue, User
from schemas import (
    DeviceCreate, Device as DeviceSchema, DeviceUpdate,
    CommandRequest, CommandLogOut, FileOperation,
    ProcessRequest, ClipboardRequest, DeviceOut
)
from utils import get_current_user, verify_device_token
import logging

router = APIRouter(prefix="/devices", tags=["Devices"])
logger = logging.getLogger(__name__)

@router.post("/{device_id}/execute", response_model=CommandLogOut)
async def execute_command(device_id: int, request: CommandRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    device = await db.execute(select(Device).where(Device.id == device_id, Device.user_id == user.id))
    device = device.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or unauthorized")
    
    if device.status == "offline":
        queued_command = CommandQueue(device_id=device_id, command=request.command)
        db.add(queued_command)
        await db.commit()
        logger.info(f"Queued command '{request.command}' for offline device {device_id}")
        return {"message": "Device offline, command queued"}
    
    # Placeholder for actual command execution
    output = f"Executed '{request.command}' on device {device_id}"
    command_log = CommandLog(device_id=device_id, command=request.command, output=output)
    device.last_seen = datetime.utcnow()
    db.add(command_log)
    await db.commit()
    await db.refresh(command_log)
    logger.info(f"User {user.username} executed '{request.command}' on device {device_id}")
    return command_log

@router.post("/{device_id}/processes")
async def manage_processes(device_id: int, request: ProcessRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    device = await db.execute(select(Device).where(Device.id == device_id, Device.user_id == user.id))
    device = device.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or unauthorized")
    
    # Placeholder for process management logic
    output = f"{request.action} process '{request.process_name or 'all'}' on device {device_id}"
    command_log = CommandLog(device_id=device_id, command=f"process_{request.action}", output=output)
    await db.add(command_log)
    await db.commit()
    return {"status": "success", "output": output}

@router.post("/{device_id}/files")
async def file_operations(device_id: int, request: FileOperation, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    device = await db.execute(select(Device).where(Device.id == device_id, Device.user_id == user.id))
    device = device.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or unauthorized")
    
    # Placeholder for file operation logic
    output = f"{request.operation} file '{request.filename}' on device {device_id}"
    command_log = CommandLog(device_id=device_id, command=f"file_{request.operation}", output=output)
    await db.add(command_log)
    await db.commit()
    return {"status": "success", "output": output}

@router.post("/{device_id}/clipboard")
async def clipboard_access(device_id: int, request: ClipboardRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    device = await db.execute(select(Device).where(Device.id == device_id, Device.user_id == user.id))
    device = device.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or unauthorized")
    
    # Placeholder for clipboard logic
    output = "Clipboard content" if request.action == "get" else f"Set clipboard to '{request.content}'"
    command_log = CommandLog(device_id=device_id, command=f"clipboard_{request.action}", output=output)
    await db.add(command_log)
    await db.commit()
    return {"status": "success", "output": output}

@router.post("/{device_id}/reboot")
async def reboot_device(device_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    device = await db.execute(select(Device).where(Device.id == device_id, Device.user_id == user.id))
    device = device.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or unauthorized")
    
    # Placeholder for reboot logic
    command_log = CommandLog(device_id=device_id, command="reboot", output="Device reboot initiated")
    await db.add(command_log)
    await db.commit()
    return {"status": "success"}

@router.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: int, token: str, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    device = await verify_device_token(device_id, token, db)
    device.status = "online"
    device.last_seen = datetime.utcnow()
    await db.commit()
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle live data streaming (status, GPS, screen, keylogging, audio)
            await websocket.send_text(f"Device {device_id} received: {data}")
            logger.info(f"WebSocket data from device {device_id}: {data}")
    except Exception as e:
        device.status = "offline"
        await db.commit()
        logger.error(f"WebSocket error for device {device_id}: {str(e)}")
        await websocket.close()