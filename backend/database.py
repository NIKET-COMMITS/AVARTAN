"""
DATABASE CONNECTION

Sets up connection to SQLite database.
Creates sessions for API endpoints.
Optimized for zero-budget/free-tier hosting concurrency.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import logging

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./avartan.db")

# Create engine (connection pool)
is_sqlite = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    # Added timeout=15 to prevent "database is locked" errors on free-tier SQLite
    connect_args={"check_same_thread": False, "timeout": 15} if is_sqlite else {},
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

def init_facilities():
    """
    Injects sample facilities into the database if it's empty.
    Manages its own safe database session to prevent memory leaks.
    """
    db_session = SessionLocal()
    logger = logging.getLogger("avartan")
    
    try:
        # Check if facilities already exist
        existing = db_session.query(Facility).first()
        if not existing:
            logger.info("Initializing sample facilities...")
            
            for fac_data in FACILITIES_DATA:
                db_facility = Facility(**fac_data)
                db_session.add(db_facility)
            
            db_session.commit()
            logger.info("Successfully loaded sample facilities!")
    except Exception as e:
        logger.error(f"Failed to initialize facilities: {e}")
        db_session.rollback()
    finally:
        # Safely close the independent session
        db_session.close()