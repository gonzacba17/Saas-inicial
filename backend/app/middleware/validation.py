"""
Strict input validation middleware and utilities
Provides comprehensive validation for all API inputs
"""

import re
import html
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, Request, status
from pydantic import BaseModel, field_validator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ValidationError(HTTPException):
    """Custom validation error exception"""
    def __init__(self, detail: str, field: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error{f' in field {field}' if field else ''}: {detail}"
        )


class InputSanitizer:
    """Utilities for sanitizing and validating inputs"""
    
    # Common regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?[1-9]\d{1,14}$')  # E.164 format
    UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    URL_PATTERN = re.compile(r'^https?://(?:[-\w.])+(?::\d+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$')
    
    # Dangerous patterns to block
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\'\s*(OR|AND)\s+\'\d+\'\s*=\s*\'\d+\')",
    ]
    
    XSS_PATTERNS = [
        r"<\s*script[^>]*>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
    ]
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000, allow_html: bool = False) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            raise ValidationError("Input must be a string")
        
        # Check length
        if len(value) > max_length:
            raise ValidationError(f"Input too long (max {max_length} characters)")
        
        # Remove null bytes and control characters
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential SQL injection attempt: {value[:100]}")
                raise ValidationError("Invalid characters detected")
        
        # Check for XSS patterns
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Potential XSS attempt: {value[:100]}")
                raise ValidationError("Invalid script content detected")
        
        # HTML escape if not allowing HTML
        if not allow_html:
            value = html.escape(value)
        
        # Strip whitespace
        value = value.strip()
        
        return value
    
    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate and sanitize email"""
        email = cls.sanitize_string(email, max_length=254)
        
        if not cls.EMAIL_PATTERN.match(email):
            raise ValidationError("Invalid email format")
        
        return email.lower()
    
    @classmethod
    def validate_phone(cls, phone: str) -> str:
        """Validate and sanitize phone number"""
        # Remove all non-digit characters except +
        phone = re.sub(r'[^\d+]', '', phone)
        
        if not cls.PHONE_PATTERN.match(phone):
            raise ValidationError("Invalid phone number format")
        
        return phone
    
    @classmethod
    def validate_url(cls, url: str) -> str:
        """Validate and sanitize URL"""
        url = cls.sanitize_string(url, max_length=2048)
        
        if not cls.URL_PATTERN.match(url):
            raise ValidationError("Invalid URL format")
        
        # Ensure HTTPS for external URLs
        if not url.startswith(('http://localhost', 'http://127.0.0.1', 'https://')):
            raise ValidationError("Only HTTPS URLs are allowed for external sites")
        
        return url
    
    @classmethod
    def validate_uuid(cls, uuid_str: str) -> str:
        """Validate UUID format"""
        uuid_str = cls.sanitize_string(uuid_str, max_length=36)
        
        if not cls.UUID_PATTERN.match(uuid_str):
            raise ValidationError("Invalid UUID format")
        
        return uuid_str.lower()
    
    @classmethod
    def validate_numeric(cls, value: Union[int, float, str], min_val: Optional[float] = None, max_val: Optional[float] = None) -> Union[int, float]:
        """Validate numeric input"""
        try:
            if isinstance(value, str):
                # Remove whitespace and check for valid numeric string
                value = value.strip()
                if not re.match(r'^-?\d+(\.\d+)?$', value):
                    raise ValidationError("Invalid numeric format")
                value = float(value) if '.' in value else int(value)
            
            if not isinstance(value, (int, float)):
                raise ValidationError("Value must be numeric")
            
            if min_val is not None and value < min_val:
                raise ValidationError(f"Value must be at least {min_val}")
            
            if max_val is not None and value > max_val:
                raise ValidationError(f"Value must be at most {max_val}")
            
            return value
        except (ValueError, TypeError):
            raise ValidationError("Invalid numeric value")
    
    @classmethod
    def validate_date(cls, date_str: str) -> datetime:
        """Validate date string"""
        date_str = cls.sanitize_string(date_str, max_length=50)
        
        # Try common date formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%fZ',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValidationError("Invalid date format")
    
    @classmethod
    def validate_file_name(cls, filename: str) -> str:
        """Validate file name"""
        filename = cls.sanitize_string(filename, max_length=255)
        
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'\.\.', '', filename)  # Remove directory traversal
        
        if not filename or filename in ['.', '..']:
            raise ValidationError("Invalid filename")
        
        # Check for dangerous file extensions
        dangerous_extensions = [
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
            '.jar', '.jsp', '.php', '.asp', '.aspx', '.sh', '.py', '.rb'
        ]
        
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        if f'.{ext}' in dangerous_extensions:
            raise ValidationError("File type not allowed")
        
        return filename


class StrictValidationMixin:
    """Mixin for Pydantic models with strict validation"""
    
    @field_validator('*', mode='before')
    @classmethod
    def validate_all_fields(cls, v, info):
        """Apply strict validation to all string fields"""
        if isinstance(v, str) and info.field_name:
            # Get field info
            field_info = cls.model_fields.get(info.field_name)
            max_length = 1000  # default
            
            # Check for string length constraints
            if field_info and hasattr(field_info, 'constraints'):
                max_length = getattr(field_info.constraints, 'max_length', max_length)
            
            # Apply sanitization
            try:
                return InputSanitizer.sanitize_string(v, max_length=max_length)
            except ValidationError as e:
                raise ValueError(f"Field '{info.field_name}': {e.detail}")
        
        return v


class ValidationMiddleware:
    """Middleware for request validation"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Validate request size
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
                await self._send_error(send, "Request too large")
                return
            
            # Validate content type for POST/PUT requests
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.headers.get("content-type", "")
                if not content_type.startswith(("application/json", "multipart/form-data", "application/x-www-form-urlencoded")):
                    await self._send_error(send, "Invalid content type")
                    return
            
            # Validate headers
            for header_name, header_value in request.headers.items():
                if len(header_value) > 8192:  # 8KB limit for headers
                    await self._send_error(send, "Header too large")
                    return
                
                # Check for suspicious header content
                if re.search(r'[<>"\']', header_value):
                    logger.warning(f"Suspicious header content: {header_name}: {header_value[:100]}")
        
        await self.app(scope, receive, send)
    
    async def _send_error(self, send, message: str):
        """Send error response"""
        response = {
            "type": "http.response.start",
            "status": 400,
            "headers": [(b"content-type", b"application/json")],
        }
        await send(response)
        
        body = f'{{"detail": "{message}"}}'
        await send({
            "type": "http.response.body",
            "body": body.encode(),
        })


# Utility functions for common validations
def validate_business_name(name: str) -> str:
    """Validate business name"""
    name = InputSanitizer.sanitize_string(name, max_length=100)
    
    if len(name) < 2:
        raise ValidationError("Business name must be at least 2 characters")
    
    if not re.match(r'^[a-zA-Z0-9\s\-\.&áéíóúñÁÉÍÓÚÑ]+$', name):
        raise ValidationError("Business name contains invalid characters")
    
    return name


def validate_product_name(name: str) -> str:
    """Validate product name"""
    name = InputSanitizer.sanitize_string(name, max_length=100)
    
    if len(name) < 1:
        raise ValidationError("Product name is required")
    
    if not re.match(r'^[a-zA-Z0-9\s\-\.&áéíóúñÁÉÍÓÚÑ]+$', name):
        raise ValidationError("Product name contains invalid characters")
    
    return name


def validate_price(price: Union[int, float, str]) -> float:
    """Validate price value"""
    price = InputSanitizer.validate_numeric(price, min_val=0, max_val=999999.99)
    
    # Round to 2 decimal places
    return round(float(price), 2)


def validate_description(description: str) -> str:
    """Validate description field"""
    description = InputSanitizer.sanitize_string(description, max_length=1000)
    
    # Allow some basic formatting but escape HTML
    description = html.escape(description)
    
    return description


def validate_password(password: str) -> str:
    """Validate password strength"""
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    
    if len(password) > 128:
        raise ValidationError("Password must be less than 128 characters")
    
    # Check for basic password requirements
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter")
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter")
    
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one number")
    
    # Check for common weak passwords
    weak_passwords = ['password', '12345678', 'qwerty123', 'admin123', 'password123']
    if password.lower() in weak_passwords:
        raise ValidationError("Password is too common")
    
    return password