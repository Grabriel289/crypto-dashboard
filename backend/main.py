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

# Use Render's PORT env var or default to 8001 locally
settings.API_PORT = int(os.environ.get('PORT', os.environ.get('API_PORT', 8001)))


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
    description="Real-time crypto market monitoring with macro analysis and sector rotation - v2.1 with Final Verdict",
    version="2.1.0",
    lifespan=lifespan
)

# CORS middleware - allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add cache-control headers to prevent caching of API responses
@app.middleware("http")
async def add_cache_control_headers(request, call_next):
    response = await call_next(request)
    # Don't cache API responses
    if request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# API routes
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.1.0", "features": ["macro", "crypto_pulse", "sectors", "key_levels", "liquidation", "stablecoin", "calendar", "correlation", "final_verdict"]}


# Serve static files (frontend build) - must be AFTER API routes
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")


@app.get("/")
async def root():
    """Root endpoint - serve frontend if available."""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Crypto Dashboard API - Visit /docs for API documentation"}


# Mount static files last - this catches all unmatched routes
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
