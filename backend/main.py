from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from init_db import init_db
import asyncio

app = FastAPI(
    title="Fatakeshto Application API",
    description="A FastAPI-based backend system for managing remote devices",
    version="1.0.0"
)

# Configure CORS and Security Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fatakeshto.vercel.app", "http://localhost:5173", "https://*.vercel.app"],  # Allow Vercel preview deployments
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Authorization", "Content-Type", "Accept", "Origin", 
        "X-Requested-With", "X-CSRF-Token", "X-Auth-Token",
        "Access-Control-Allow-Credentials", "Access-Control-Allow-Origin"
    ],
    expose_headers=["Content-Length", "Content-Range", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=7200  # Increase cache time to 2 hours
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return JSONResponse({"status": "healthy"})

# Import and include routers
from routers import auth, devices, admin

# Mount authentication router with proper prefix and tags
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

# Mount devices router
app.include_router(
    devices.router,
    prefix="/api/devices",
    tags=["Devices"]
)

# Mount admin router
app.include_router(
    admin.router,
    prefix="/api/admin",
    tags=["Admin"]
)

@app.on_event("startup")
async def startup_event():
    # Initialize the database
    await init_db()
    print("Database initialized successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)