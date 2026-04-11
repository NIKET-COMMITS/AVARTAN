"""
Logging System - Production Grade

Logs all requests and errors safely.
Never logs sensitive data (passwords, tokens, API keys).
Includes rotating file handler to prevent huge log files.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from backend.config import settings

# Create logs directory
os.makedirs("logs", exist_ok=True)

# Create logger
logger = logging.getLogger("avartan")
logger.setLevel(getattr(logging, settings.LOG_LEVEL))

# File handler with rotation
file_handler = logging.handlers.RotatingFileHandler(
    settings.LOG_FILE,
    maxBytes=settings.LOG_MAX_SIZE,
    backupCount=settings.LOG_BACKUP_COUNT
)

# Console handler
console_handler = logging.StreamHandler()

# Format
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log_request(endpoint: str, method: str, user_id: int = None):
    """Log API request - NEVER log body with passwords/tokens"""
    logger.info(f"REQUEST: {method} {endpoint} | User: {user_id}")


def log_error(error: str, exception: Exception = None):
    """Log error safely"""
    logger.error(f"ERROR: {error}")
    if exception and settings.DEBUG:
        logger.exception(exception)


def log_success(action: str, details: str = ""):
    """Log successful action"""
    logger.info(f"SUCCESS: {action} | {details}")


def log_warning(warning: str):
    """Log warning"""
    logger.warning(f"WARNING: {warning}")

def log_security_event(event_type: str, details: str = ""):
    """Log security event"""
    logger.warning(f"SECURITY ALERT | Type: {event_type} | Details: {details}")