from fastapi import APIRouter, Depends, HTTPException, WebSocket, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select, update
from backend.database import get_db
from backend.models import Device, CommandLog, CommandQueue
from backend.schemas import CommandRequest, CommandLogOut, FileOperation, ProcessRequest, ClipboardRequest, DeviceOut
from backend.utils import get_current_user, verify_device_token
import json
import logging

router = APIRouter(prefix="/devices", tags=["Devices"])
logger = logging.getLogger(__name__)

@router.post("/{device_id}/execute", response_model=CommandLogOut)
async def execute_command(device_id: int, request: CommandRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Device).where(Device.id == device_id, Device.user_id == current_user.id))
    device = result.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or unauthorized")
    if device.status == "offline":
        queued_command = CommandQueue(device_id=device_id, command=request.command)
        db.add(queued_command)
        await db.commit()
        logger.info(f"Queued command '{request.command}' for offline device {device_id}")
        return {"message": "Device offline, command queued"}
    output = f"Executed '{request.command}' on device {device_id}"
    command_log = CommandLog(device_id=device_id, command=request.command, output=output)
    device.last_seen = datetime.utcnow()
    db.add(command_log)
    await db.commit()
    await db.refresh(command_log)
    logger.info(f"User {current_user.username} executed '{request.command}' on device {device_id}")
    return command_log

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
            # Handle live data streaming
            await websocket.send_text(f"Device {device_id} received: {data}")
            logger.info(f"WebSocket data from device {device_id}: {data}")
    except Exception as e:
        device.status = "offline"
        await db.commit()
        logger.error(f"WebSocket error for device {device_id}: {str(e)}")
        await websocket.close()