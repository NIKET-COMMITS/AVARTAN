"""
Configuration Management - Production Safe

Uses environment variables for sensitive data.
Never hardcodes secrets.
Validates configuration on startup.
"""

import os
from dotenv import load_dotenv
from enum import Enum

# Load environment variables from .env file
load_dotenv()


class Environment(str, Enum):
    """Application environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings:
    """
    Application settings loaded from environment
    
    SECURITY FEATURES:
    - All sensitive data from environment variables
    - No hardcoded secrets
    - Defaults are safe for development
    - Production requires explicit configuration
    - Validation on startup
    """
    MAX_DESCRIPTION_LENGTH: int = int(os.getenv("MAX_DESCRIPTION_LENGTH", "500"))
    # ============ ENVIRONMENT ============
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # ============ DATABASE ============
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./avartan.db")
    
    # ============ SECURITY ============
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    if not SECRET_KEY or len(SECRET_KEY) < 32:
        if ENVIRONMENT == "production":
            raise ValueError(
                "ERROR: SECRET_KEY not set or too short!\n"
                "Set in .env file: SECRET_KEY=your-secret-key-min-32-chars\n"
                "Use: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
            
    # ============ RATE LIMITING ============
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
    LOGIN_ATTEMPTS_LIMIT: int = int(os.getenv("LOGIN_ATTEMPTS_LIMIT", "5"))
    
    # ============ AI CONFIGURATION ============
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    GEMINI_MAX_TOKENS: int = int(os.getenv("GEMINI_MAX_TOKENS", "1024"))
    GEMINI_TIMEOUT_SECONDS: int = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "30"))
    
    # ============ LOGGING ============
    LOG_FILE: str = "logs/avartan.log"
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # ============ CORS ============
    CORS_ORIGINS: list = [
        "http://localhost:8050",
        "http://localhost:3000",
        "http://127.0.0.1:8050",
    ]
    
    @staticmethod
    def validate_production():
        """Validate production configuration"""
        if Settings.ENVIRONMENT == "production":
            assert Settings.SECRET_KEY and len(Settings.SECRET_KEY) >= 32, "Invalid SECRET_KEY"
            assert Settings.GEMINI_API_KEY, "GEMINI_API_KEY required"
            assert Settings.DEBUG is False, "DEBUG must be False in production"
    
    @staticmethod
    def get_settings() -> "Settings":
        """Get current settings"""
        return Settings()

# Initialize settings
settings = Settings.get_settings()