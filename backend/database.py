"""
DATABASE CONNECTION

Sets up connection to SQLite database.
Creates sessions for API endpoints.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database configuration
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./avartan.db")

# Create engine (connection pool)
is_sqlite = DATABASE_URL.startswith("sqlite")
engine = create_engine(
    DATABASE_URL,
    # Only apply "check_same_thread" if we are actually using SQLite
    connect_args={"check_same_thread": False} if is_sqlite else {},
    # pool_pre_ping ensures the connection is still alive before using it
    pool_pre_ping=True,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    """
    Dependency function that FastAPI calls automatically.
    
    Every endpoint that needs database gets session through this.
    Session automatically closes after endpoint finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ PHASE 3: FACILITY INJECTOR ============
from backend.models import Facility
from backend.data.facilities_data import FACILITIES_DATA
import logging

def init_facilities(db_session):
    """Injects sample facilities into the database if it's empty."""
    try:
        # Check if facilities already exist
        existing = db_session.query(Facility).first()
        if not existing:
            logger = logging.getLogger("avartan")
            logger.info("Initializing sample facilities...")
            
            for fac_data in FACILITIES_DATA:
                db_facility = Facility(**fac_data)
                db_session.add(db_facility)
            
            db_session.commit()
            logger.info("Successfully loaded sample facilities!")
    except Exception as e:
        logger = logging.getLogger("avartan")
        logger.error(f"Failed to initialize facilities: {e}")
        db_session.rollback()