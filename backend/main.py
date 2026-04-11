"""
AVARTAN MAIN APP - Phase 3 (Facility Matching)
"""
import warnings
from contextlib import asynccontextmanager

# Suppress the noisy Gemini SDK warning for a clean terminal
warnings.filterwarnings("ignore", category=FutureWarning)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.routers import auth, waste, facilities
from backend.middleware import SecurityMiddleware
from backend.database import engine, SessionLocal, init_facilities
from backend.models import Base
from backend.config import settings

# Setup standard logger
logger = logging.getLogger("avartan")

# 4. Modern Lifespan Event (Replaces the deprecated @app.on_event("startup"))
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Avartan Server Phase 3...")
    
    # Create all database tables
    Base.metadata.create_all(bind=engine)
    
    # Inject Sample Facilities into SQLite
    db = SessionLocal()
    try:
        init_facilities(db)
    except Exception as e:
        logger.error(f"Startup DB Injection Failed: {e}")
    finally:
        db.close()
        
    logger.info("Application startup complete.")
    yield # This hands control over to the running server

app = FastAPI(
    title="AVARTAN",
    description="AI-powered waste management platform",
    version="3.0.0",
    lifespan=lifespan # Attach the new modern lifespan handler here
)

# 1. Add Security Middleware
app.add_middleware(SecurityMiddleware)

# 2. Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Include Routers
app.include_router(auth.router)
app.include_router(waste.router)
app.include_router(facilities.router)

# 5. Health Check Endpoint
@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "environment": settings.ENVIRONMENT,
        "ai_active": settings.GEMINI_API_KEY != "",
        "phase": "Phase 3: Facility Matching Active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)