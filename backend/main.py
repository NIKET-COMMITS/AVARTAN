"""
AVARTAN FastAPI Application
Main entry point for all API endpoints
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import uuid
from datetime import datetime

from backend.logger import setup_logger
from backend.config import settings
from backend.database import engine
from backend.models import Base

# Setup logging
logger = setup_logger(__name__)

# ============ IMPORT ALL ROUTERS (9 TOTAL) ============
from backend.routers import (
    auth,
    waste,
    facilities,
    routes,
    predictions,
    dashboard,
    reports,
    leaderboard,
    profile
)

# ============ CREATE DATABASE TABLES ============
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified")
except Exception as e:
    logger.error(f"❌ Database error: {str(e)}")
    raise

# ============ CREATE FASTAPI APP ============
app = FastAPI(
    title="AVARTAN",
    description="AI-powered waste management platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ============ CORS MIDDLEWARE ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ REQUEST MIDDLEWARE ============
@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Add request ID and timing"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    start_time = datetime.utcnow()
    response = await call_next(request)
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(duration)
    logger.info(f"[{request_id}] {response.status_code} ({duration:.3f}s)")
    
    return response

# ============ EXCEPTION HANDLERS ============
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation Error",
            "message": "Invalid request data"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )

# ============ INCLUDE ALL ROUTERS ============
app.include_router(auth.router, tags=["authentication"])
app.include_router(waste.router, tags=["waste"])
app.include_router(facilities.router, tags=["facilities"])
app.include_router(routes.router, tags=["routes"])
app.include_router(predictions.router, tags=["ml"])
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(reports.router, tags=["reports"])
app.include_router(leaderboard.router, tags=["leaderboard"])
app.include_router(profile.router, tags=["profile"])

# ============ HEALTH CHECK ENDPOINTS ============
@app.get("/", tags=["health"])
async def root():
    """Root endpoint"""
    return {
        "success": True,
        "data": {
            "name": "AVARTAN",
            "version": "1.0.0",
            "documentation": "http://localhost:8000/docs"
        }
    }

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",          # Moved to the top level!
        "success": True,
        "data": {
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT
        }
    }

# ============ STARTUP & SHUTDOWN ============
@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    logger.info("=" * 60)
    logger.info("🚀 AVARTAN Starting...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("✅ AVARTAN Ready! Access at http://localhost:8000")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    logger.info("🛑 AVARTAN Shutting Down...")

# ============ RUN SERVER ============
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )