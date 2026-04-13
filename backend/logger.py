"""
Logger Configuration - Complete
Sets up structured logging with all required helper functions
NO EMOJIS - Plain text for Windows compatibility
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# ============ LOGGER SETUP ============

def get_logger(name):
    """Get or create a logger instance"""
    return logging.getLogger(name)

def setup_logger(name):
    """
    Configure logger with file and console handlers
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Console handler
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        
        # File handler with UTF-8 encoding
        file_handler = RotatingFileHandler(
            "logs/avartan.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger

# ============ LOGGING HELPER FUNCTIONS ============

def log_success(context: str, message: str):
    """Log success message (plain text, no emojis)"""
    logger = get_logger(__name__)
    logger.info(f"[SUCCESS] [{context}] {message}")

def log_error(message: str, context: str = "ERROR"):
    """Log error message (plain text, no emojis)"""
    logger = get_logger(__name__)
    logger.error(f"[ERROR] [{context}] {message}")

def log_warning(context: str, message: str):
    """Log warning message (plain text, no emojis)"""
    logger = get_logger(__name__)
    logger.warning(f"[WARNING] [{context}] {message}")

def log_info(context: str, message: str):
    """Log info message (plain text, no emojis)"""
    logger = get_logger(__name__)
    logger.info(f"[INFO] [{context}] {message}")

def log_request(method: str, endpoint: str, status_code: int = None):
    """
    Log API request
    
    Args:
        method: HTTP method (GET, POST, etc)
        endpoint: API endpoint path
        status_code: HTTP response status code
    """
    logger = get_logger(__name__)
    if status_code:
        logger.info(f"[REQUEST] {method} {endpoint} -> {status_code}")
    else:
        logger.info(f"[REQUEST] {method} {endpoint}")

def log_security_event(event_type: str, details: str):
    """
    Log security-related event
    
    Args:
        event_type: Type of security event (login_attempt, auth_failure, etc)
        details: Details about the event
    """
    logger = get_logger(__name__)
    logger.warning(f"[SECURITY] [{event_type}] {details}")

# Initialize default logger
logger = setup_logger(__name__)