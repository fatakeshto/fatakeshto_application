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
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return JSONResponse({"status": "healthy"})

# Import and include routers
from routers import auth, devices, admin
app.include_router(auth.router)
app.include_router(devices.router, prefix="/devices", tags=["Devices"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)