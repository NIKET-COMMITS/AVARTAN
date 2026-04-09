"""
DATABASE CONNECTION

Sets up connection to SQLite database.
Creates sessions for API endpoints.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "sqlite:///./avartan.db"

# Create engine (connection pool)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
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