from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select, delete
from .database import get_db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def periodic_data_collection(db: AsyncSession):
    logger.info("Starting periodic data collection")
    result = await db.execute(select(Device))
    devices = result.scalars().all()
    for device in devices:
        device.last_seen = datetime.utcnow()
    await db.commit()
    logger.info("Completed periodic data collection")

async def auto_reconnect_devices(db: AsyncSession):
    logger.info("Starting auto-reconnect task")
    result = await db.execute(select(Device).where(Device.status == "offline"))
    devices = result.scalars().all()
    for device in devices:
        device.status = "online"
        await db.commit()
    logger.info("Completed auto-reconnect task")

async def process_command_queue(db: AsyncSession):
    logger.info("Processing command queue")
    result = await db.execute(select(CommandQueue).where(CommandQueue.status == "pending"))
    commands = result.scalars().all()
    for cmd in commands:
        device = await db.execute(select(Device).where(Device.id == cmd.device_id))
        device = device.scalars().first()
        if device and device.status == "online":
            output = f"Executed queued command '{cmd.command}'"
            command_log = CommandLog(device_id=cmd.device_id, command=cmd.command, output=output)
            cmd.status = "executed"
            db.add(command_log)
            await db.commit()
    logger.info("Completed command queue processing")

async def cleanup_old_logs(db: AsyncSession):
    logger.info("Starting log cleanup")
    threshold = datetime.utcnow() - timedelta(days=30)
    await db.execute(delete(CommandLog).where(CommandLog.timestamp < threshold))
    await db.commit()
    logger.info("Completed log cleanup")

def start_scheduler():
    scheduler.add_job(periodic_data_collection, "interval", minutes=5, args=[get_db()])
    scheduler.add_job(auto_reconnect_devices, "interval", minutes=10, args=[get_db()])
    scheduler.add_job(process_command_queue, "interval", minutes=1, args=[get_db()])
    scheduler.add_job(cleanup_old_logs, "interval", days=1, args=[get_db()])
    scheduler.start()
    logger.info("Background scheduler started")