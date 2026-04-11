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