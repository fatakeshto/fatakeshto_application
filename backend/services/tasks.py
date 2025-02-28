from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select, delete
from datetime import datetime, timedelta
from database import AsyncSessionLocal
from models import Device, CommandQueue, CommandLog
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def periodic_data_collection():
    async for db in get_session():
        try:
            logger.info("Starting periodic data collection")
            result = await db.execute(select(Device))
            devices = result.scalars().all()
            for device in devices:
                device.last_seen = datetime.utcnow()
            await db.commit()
            logger.info("Completed periodic data collection")
        except Exception as e:
            logger.error(f"Error in periodic data collection: {e}")
            await db.rollback()

async def auto_reconnect_devices():
    async for db in get_session():
        try:
            logger.info("Starting auto-reconnect task")
            result = await db.execute(select(Device).where(Device.status == "offline"))
            devices = result.scalars().all()
            for device in devices:
                device.status = "online"
            await db.commit()
            logger.info("Completed auto-reconnect task")
        except Exception as e:
            logger.error(f"Error in auto-reconnect task: {e}")
            await db.rollback()

async def process_command_queue():
    async for db in get_session():
        try:
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
        except Exception as e:
            logger.error(f"Error in command queue processing: {e}")
            await db.rollback()

async def cleanup_old_logs():
    async for db in get_session():
        try:
            logger.info("Starting log cleanup")
            threshold = datetime.utcnow() - timedelta(days=30)
            await db.execute(delete(CommandLog).where(CommandLog.timestamp < threshold))
            await db.commit()
            logger.info("Completed log cleanup")
        except Exception as e:
            logger.error(f"Error in log cleanup: {e}")
            await db.rollback()

def start_scheduler():
    scheduler.add_job(periodic_data_collection, "interval", minutes=5)
    scheduler.add_job(auto_reconnect_devices, "interval", minutes=10)
    scheduler.add_job(process_command_queue, "interval", minutes=1)
    scheduler.add_job(cleanup_old_logs, "interval", days=1)
    scheduler.start()
    logger.info("Background scheduler started")