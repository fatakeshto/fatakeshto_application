from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Fatakeshto Application API",
    description="A FastAPI-based backend system for managing remote devices",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fatakeshto-application.vercel.app"],  # Only allow the Vercel deployment URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)