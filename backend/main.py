from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database import engine, Base, get_db
from routers import auth, devices, admin
from services import tasks
import logging
from logging.handlers import RotatingFileHandler
from collections import defaultdict
import time

app = FastAPI(title="Device Management Backend")

# Configure logging with rotation
log_handler = RotatingFileHandler("app.log", maxBytes=1000000, backupCount=10)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)
logging.getLogger().addHandler(log_handler)
app.logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMIT = 500  # Increased for production
RATE_LIMIT_WINDOW = 60
request_counts = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = time.time()
    request_times = request_counts[client_ip]
    request_times = [t for t in request_times if now - t < RATE_LIMIT_WINDOW]
    if len(request_times) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    request_times.append(now)
    request_counts[client_ip] = request_times
    response = await call_next(request)
    return response

# Include routers
app.include_router(auth.router, prefix="/auth")
app.include_router(devices.router, prefix="/devices")
app.include_router(admin.router, prefix="/admin")

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    tasks.start_scheduler()
    app.logger.info("Application started, database initialized, and scheduler running")

@app.get("/")
async def root():
    return {"message": "Device Management Backend is running"}