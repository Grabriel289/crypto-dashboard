"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import asyncio

from config.settings import settings
from api.routes import dashboard
from data.scheduler import data_scheduler, data_cache
import os

# Force port change to avoid conflict
os.environ['API_PORT'] = '8001'
settings.API_PORT = 8001


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print(f">>> Starting Crypto Dashboard API on port {settings.API_PORT}...")
    
    # Start scheduler and run initial fetch
    data_scheduler.start()
    await data_scheduler.run_initial_fetch()
    
    yield
    
    # Shutdown
    print(">>> Shutting down...")
    data_scheduler.stop()


app = FastAPI(
    title="Crypto Market Dashboard API",
    description="Real-time crypto market monitoring with macro analysis and sector rotation",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}


# Serve static files (frontend build)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")


@app.get("/")
async def root():
    """Root endpoint - serve frontend if available."""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Crypto Dashboard API - Visit /docs for API documentation"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
