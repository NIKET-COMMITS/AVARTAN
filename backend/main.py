"""
MAIN APP FILE

Creates FastAPI application.
Sets up all configuration.
Includes all routes.
Creates database tables.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import auth
from backend.database import engine
from backend.models import Base

# Create all database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="AVARTAN",
    description="AI-powered waste management platform",
    version="1.0.0"
)

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8050", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth.router)

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to AVARTAN",
        "docs": "/docs"
    }

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )