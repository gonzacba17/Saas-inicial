"""
CSRF Protection Middleware
Double Submit Cookie pattern implementation
"""
import secrets
import hmac
import hashlib
from typing import Optional
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import MutableHeaders
from app.core.config import settings


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection using Double Submit Cookie pattern.
    
    For state-changing requests (POST, PUT, DELETE, PATCH), validates that:
    1. A CSRF token cookie exists
    2. The request includes a matching CSRF token header
    3. The tokens match and are valid
    """
    
    def __init__(
        self,
        app,
        cookie_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        secret_key: Optional[str] = None
    ):
        super().__init__(app)
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.secret_key = secret_key or settings.secret_key
        self.safe_methods = {"GET", "HEAD", "OPTIONS", "TRACE"}
        
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF for testing
        if settings.testing:
            return await call_next(request)
            
        # Skip CSRF for safe methods and health checks
        if request.method in self.safe_methods or request.url.path.startswith("/health"):
            response = await call_next(request)
            # Set CSRF cookie on safe requests if not present
            if self.cookie_name not in request.cookies:
                token = self._generate_token()
                response.set_cookie(
                    key=self.cookie_name,
                    value=token,
                    httponly=True,
                    secure=settings.environment == "production",
                    samesite="lax",
                    max_age=3600 * 24  # 24 hours
                )
            return response
        
        # Validate CSRF token for state-changing requests
        cookie_token = request.cookies.get(self.cookie_name)
        header_token = request.headers.get(self.header_name)
        
        # Check if tokens exist
        if not cookie_token or not header_token:
            raise HTTPException(
                status_code=403,
                detail="CSRF token missing"
            )
        
        # Validate tokens match
        if not self._tokens_match(cookie_token, header_token):
            raise HTTPException(
                status_code=403,
                detail="CSRF token invalid"
            )
        
        # Tokens valid, proceed with request
        response = await call_next(request)
        
        # Rotate CSRF token after successful state-changing request
        new_token = self._generate_token()
        response.set_cookie(
            key=self.cookie_name,
            value=new_token,
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax",
            max_age=3600 * 24
        )
        
        return response
    
    def _generate_token(self) -> str:
        """Generate a cryptographically secure CSRF token."""
        return secrets.token_urlsafe(32)
    
    def _tokens_match(self, cookie_token: str, header_token: str) -> bool:
        """
        Constant-time comparison of CSRF tokens.
        Prevents timing attacks.
        """
        return hmac.compare_digest(cookie_token, header_token)


class CSRFProtect:
    """
    Helper class for generating CSRF tokens in responses.
    Use this to include CSRF tokens in API responses.
    """
    
    @staticmethod
    def generate_token() -> str:
        """Generate a new CSRF token."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def set_csrf_cookie(response: Response, token: str, secure: bool = False):
        """Set CSRF token cookie on response."""
        response.set_cookie(
            key="csrf_token",
            value=token,
            httponly=True,
            secure=secure,
            samesite="lax",
            max_age=3600 * 24
        )
        return response
