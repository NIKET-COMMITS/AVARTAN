"""
AVARTAN FastAPI Application
Main entry point for all API endpoints
"""

import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from backend.logger import setup_logger
from backend.config import settings
from backend.database import engine, SessionLocal  
from backend.models import Base, Facility          

# Setup logging
logger = setup_logger(__name__)

# ============ IMPORT ALL ROUTERS ============
from backend.routers import (
    auth, waste, facilities, routes, predictions, 
    dashboard, reports, leaderboard, profile, marketplace
)

# ============ LIFESPAN (Modern Startup/Shutdown) ============
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events using FastAPI's modern lifespan context manager.
    """
    logger.info("=" * 60)
    logger.info("🚀 AVARTAN Starting...")
    
    # Create DB Tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Database error: {str(e)}")
        raise

    # Seed Gandhinagar Data
    db = SessionLocal()
    try:
        if db.query(Facility).count() == 0:
            logger.info("🌱 Database empty. Seeding Gandhinagar Facilities...")
            gandhinagar_facilities = [
                # === REPAIR FACILITIES ===
                Facility(name="PDEU Tech Repair Hub", address="Knowledge Corridor, near PDEU Gate 1, Raisan", city="Gandhinagar", latitude=23.1557, longitude=72.6620, rating=4.9, materials_accepted=["Repair", "Laptops", "Phones", "E-Waste"], is_open=True),
                Facility(name="Sargasan Mobile Hospital", address="Pramukh Arcade, Sargasan Cross Road", city="Gandhinagar", latitude=23.1783, longitude=72.6362, rating=4.6, materials_accepted=["Repair", "Screen Replacement", "Motherboard"], is_open=True),
                Facility(name="Sector 16 Appliance Fix-It", address="District Shopping Centre, Sector 16", city="Gandhinagar", latitude=23.2355, longitude=72.6455, rating=4.3, materials_accepted=["Repair", "Electronics", "Mixed"], is_open=True),

                # === SELL FACILITIES ===
                Facility(name="Cashify Store - InfoCity", address="Super Mall 1, Ground Floor, InfoCity", city="Gandhinagar", latitude=23.1878, longitude=72.6288, rating=4.8, materials_accepted=["Sell", "Phones", "Laptops", "E-Waste"], is_open=True),
                Facility(name="Kudasan Pre-Owned Electronics", address="Swagat Rainforest 2, Kudasan", city="Gandhinagar", latitude=23.1872, longitude=72.6368, rating=4.4, materials_accepted=["Sell", "Working Tech", "Appliances"], is_open=True),
                Facility(name="Reliance Digital Exchange", address="Promenade Mall, Sector 11", city="Gandhinagar", latitude=23.2167, longitude=72.6517, rating=4.5, materials_accepted=["Sell", "Smartphones", "TVs"], is_open=True),

                # === RECYCLE FACILITIES ===
                Facility(name="GIDC Phase 2 E-Waste Yard", address="Plot 402, GIDC Electronic Estate, Sector 25", city="Gandhinagar", latitude=23.2450, longitude=72.6680, rating=4.1, materials_accepted=["Recycle", "E-Waste", "Metal", "Plastic"], is_open=True),
                Facility(name="Sector 21 AMC Green Hub", address="Near Government Library, Sector 21", city="Gandhinagar", latitude=23.2330, longitude=72.6520, rating=4.2, materials_accepted=["Recycle", "Paper", "Glass", "Plastic"], is_open=True),
                Facility(name="PDEU Innovation Scrapyard", address="PDEU Campus, Solar Park Road, Raisan", city="Gandhinagar", latitude=23.1565, longitude=72.6630, rating=4.7, materials_accepted=["Recycle", "Metal", "E-Waste", "Mixed"], is_open=True)
            ]
            db.add_all(gandhinagar_facilities)
            db.commit()
            logger.info("✅ Gandhinagar Seed Data Injected Successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to seed data: {e}")
        db.rollback()
    finally:
        db.close()

    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("✅ AVARTAN Ready! Access at http://localhost:8000")
    logger.info("=" * 60)
    
    yield # App runs here
    
    # Shutdown logic
    logger.info("🛑 AVARTAN Shutting Down cleanly...")

# ============ CREATE FASTAPI APP ============
app = FastAPI(
    title="AVARTAN",
    description="AI-powered waste management platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan # Injects the startup/shutdown logic above
)

# ============ COMPRESSION MIDDLEWARE ============
# Compresses responses > 1000 bytes to save bandwidth
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ============ CORS MIDDLEWARE ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    """Add request ID and precise timing headers"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    logger.info(f"[{request_id}] Incoming {request.method} {request.url.path}")
    
    start_time = datetime.utcnow()
    response = await call_next(request)
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration:.4f}"
    logger.info(f"[{request_id}] Completed {response.status_code} ({duration:.4f}s)")
    
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Standardize HTTP error payloads across all endpoints."""
    message = str(exc.detail) if exc.detail else "Request failed."
    error_map = {
        400: "Bad Request",
        401: "Unauthorized",
        404: "Not Found",
        500: "Internal Server Error",
    }
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": message,
            "error": error_map.get(exc.status_code, "HTTP Error"),
        },
    )


# ============ EXCEPTION HANDLERS ============
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors elegantly"""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all for internal server errors"""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred."
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
app.include_router(marketplace.router, tags=["marketplace"])

# ============ HEALTH CHECK ENDPOINTS ============
@app.get("/", tags=["health"])
async def root():
    return {
        "success": True,
        "data": {
            "name": "AVARTAN",
            "version": "1.0.0",
            "status": "online",
            "documentation": "/docs"
        }
    }

@app.get("/health", tags=["health"])
async def health_check():
    return {
        "success": True,
        "data": {
            "status": "ok",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat()
        }
    }

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