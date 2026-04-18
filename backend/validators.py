"""
Input Validation & Sanitization - Security Layer

Prevents:
- SQL Injection
- XSS (Cross-Site Scripting)
- Invalid data entry
- Buffer overflow
"""

import re
from typing import Optional, Union
from backend.config import settings


class ValidationError(Exception):
    """Custom validation error"""
    pass


def sanitize_string(value: str, max_length: int = None) -> str:
    """
    Sanitize string input
    
    Removes:
    - Leading/trailing whitespace
    - Special characters that could cause injection
    - Extra spaces
    """
    if not isinstance(value, str):
        raise ValidationError("Input must be string")
    
    value = value.strip()
    
    if max_length and len(value) > max_length:
        raise ValidationError(f"Input exceeds {max_length} characters")
    
    # Allow alphanumeric, spaces, and safe punctuation only
    pattern = r'^[a-zA-Z0-9\s\-\.,()&]*$'
    if not re.match(pattern, value):
        raise ValidationError("Input contains invalid characters")
    
    return value


def validate_email(email: str) -> str:
    """Validate email format"""
    email = email.strip().lower()
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")
    
    if len(email) > 254:
        raise ValidationError("Email too long")
    
    return email

def validate_waste_description(description: str) -> str:
    """Validate the description before sending to AI"""
    if not description:
        raise ValidationError("Description cannot be empty")
    
    description = sanitize_string(description, 500)
    
    if len(description) < 3:
        raise ValidationError("Description too short (min 3 characters)")
    
    return description


def validate_quantity(quantity: Union[int, float]) -> float:
    """Validate quantity to support Float/KG metrics"""
    if not isinstance(quantity, (int, float)):
        raise ValidationError("Quantity must be a number")
    
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than 0")
    
    if quantity > 10000:
        raise ValidationError("Quantity cannot exceed 10000 kg")
    
    return float(quantity)


def validate_condition(condition: str) -> str:
    """Validate waste condition"""
    valid_conditions = ["mint", "good", "fair", "poor", "broken"]
    
    condition = condition.lower().strip()
    
    if condition not in valid_conditions:
        raise ValidationError(
            f"Condition must be one of: {', '.join(valid_conditions)}"
        )
    
    return condition


def sanitize_for_ai(text: str) -> str:
    """
    Sanitize text before sending to AI API
    Removes dangerous patterns.
    """
    dangerous_patterns = [
        r'<script.*?</script>',
        r'javascript:',
        r'onerror=',
        r'onclick=',
        r'<iframe',
        r'DROP TABLE',
        r'DELETE FROM',
        r'INSERT INTO'
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return sanitize_string(text, 1000)