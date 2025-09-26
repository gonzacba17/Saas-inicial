"""
Security middleware for rate limiting, CORS, and other security features.
"""
import time
import redis
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis or in-memory storage."""
    
    def __init__(self, app, calls: int = 100, period: int = 3600):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.redis_client = None
        self.redis_checked = False
        self.memory_store: Dict[str, Dict[str, float]] = {}
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and static files (ultra-fast path)
        if request.url.path.startswith("/health") or request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Check rate limit
        if self._is_rate_limited(client_ip, current_time):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again later."
            )
        
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client is rate limited."""
        # Lazy Redis initialization
        if not self.redis_checked:
            self._init_redis()
        
        if self.redis_client:
            return self._redis_rate_limit(client_ip, current_time)
        else:
            return self._memory_rate_limit(client_ip, current_time)
    
    def _init_redis(self):
        """Initialize Redis connection lazily."""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host if hasattr(settings, 'redis_host') else 'localhost',
                port=settings.redis_port if hasattr(settings, 'redis_port') else 6379,
                decode_responses=True,
                socket_connect_timeout=0.1,  # Fast timeout for connection
                socket_timeout=0.1
            )
            self.redis_client.ping()
        except Exception:
            print("Redis connection failed, using memory cache")
            self.redis_client = None
        finally:
            self.redis_checked = True
    
    def _redis_rate_limit(self, client_ip: str, current_time: float) -> bool:
        """Rate limiting using Redis."""
        key = f"rate_limit:{client_ip}"
        try:
            # Get current count
            current_count = self.redis_client.get(key)
            if current_count is None:
                # First request
                self.redis_client.setex(key, self.period, 1)
                return False
            
            if int(current_count) >= self.calls:
                return True
            
            # Increment counter
            self.redis_client.incr(key)
            return False
            
        except Exception:
            # If Redis fails, allow the request
            return False
    
    def _memory_rate_limit(self, client_ip: str, current_time: float) -> bool:
        """Rate limiting using in-memory storage."""
        if client_ip not in self.memory_store:
            self.memory_store[client_ip] = {"count": 1, "start_time": current_time}
            return False
        
        client_data = self.memory_store[client_ip]
        
        # Reset if period has passed
        if current_time - client_data["start_time"] > self.period:
            self.memory_store[client_ip] = {"count": 1, "start_time": current_time}
            return False
        
        # Check if limit exceeded
        if client_data["count"] >= self.calls:
            return True
        
        # Increment counter
        client_data["count"] += 1
        return False

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip security headers for ultra-fast health endpoints
        if request.url.path in ["/health", "/readyz"]:
            return await call_next(request)
            
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

def setup_cors(app):
    """Setup CORS middleware."""
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://your-frontend-domain.com",  # Add your production frontend domain
    ]
    
    if hasattr(settings, 'frontend_url') and settings.frontend_url:
        origins.append(settings.frontend_url)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

def setup_security_middleware(app):
    """Setup all security middleware."""
    # CORS
    setup_cors(app)
    
    # Rate limiting
    app.add_middleware(RateLimitMiddleware, calls=100, period=3600)  # 100 requests per hour
    
    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)