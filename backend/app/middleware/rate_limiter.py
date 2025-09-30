"""
Advanced rate limiting middleware with Redis support and fallback.
"""
import time
import logging
import hashlib
from typing import Dict, Optional, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis
import json
import os

logger = logging.getLogger(__name__)

class RateLimitConfig:
    """Configuration for different rate limit tiers."""
    
    # Authentication endpoints (stricter limits)
    AUTH_LIMITS = {
        "requests": 5,      # 5 requests
        "window": 300,      # per 5 minutes
        "burst": 10         # burst allowance
    }
    
    # AI endpoints (expensive operations)
    AI_LIMITS = {
        "requests": 10,     # 10 requests  
        "window": 3600,     # per hour
        "burst": 3          # minimal burst
    }
    
    # Payment endpoints (critical)
    PAYMENT_LIMITS = {
        "requests": 20,     # 20 requests
        "window": 3600,     # per hour
        "burst": 5          # limited burst
    }
    
    # General API endpoints
    GENERAL_LIMITS = {
        "requests": 100,    # 100 requests
        "window": 3600,     # per hour  
        "burst": 20         # reasonable burst
    }

class RedisRateLimiter:
    """Redis-based rate limiter with fallback to in-memory."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_store: Dict[str, Dict] = defaultdict(dict)
        self._setup_redis()
    
    def _setup_redis(self):
        """Setup Redis connection with error handling."""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=2,
                socket_connect_timeout=2,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Rate limiter connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory fallback: {e}")
            self.redis_client = None
    
    def _get_client_key(self, request: Request) -> str:
        """Generate unique client key from request."""
        # Use IP + User-Agent for better fingerprinting
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Include authenticated user if available
        user_id = ""
        if hasattr(request.state, 'user_id'):
            user_id = str(request.state.user_id)
        
        # Create hash of combined data
        combined = f"{client_ip}:{user_agent}:{user_id}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def _get_endpoint_category(self, path: str, method: str) -> str:
        """Determine rate limit category based on endpoint."""
        path_lower = path.lower()
        
        if "/auth/" in path_lower or path_lower.endswith("/login") or path_lower.endswith("/register"):
            return "auth"
        elif "/ai/" in path_lower or "openai" in path_lower:
            return "ai"
        elif "/payments/" in path_lower or "/webhook" in path_lower:
            return "payment"
        else:
            return "general"
    
    def _get_limits(self, category: str) -> Dict:
        """Get rate limit configuration for category."""
        limits_map = {
            "auth": RateLimitConfig.AUTH_LIMITS,
            "ai": RateLimitConfig.AI_LIMITS, 
            "payment": RateLimitConfig.PAYMENT_LIMITS,
            "general": RateLimitConfig.GENERAL_LIMITS
        }
        return limits_map.get(category, RateLimitConfig.GENERAL_LIMITS)
    
    async def is_allowed(self, request: Request) -> Tuple[bool, Dict]:
        """Check if request is allowed and return rate limit info."""
        client_key = self._get_client_key(request)
        category = self._get_endpoint_category(request.url.path, request.method)
        limits = self._get_limits(category)
        
        # Create Redis/memory key
        key = f"ratelimit:{category}:{client_key}"
        current_time = int(time.time())
        window_start = current_time - limits["window"]
        
        try:
            if self.redis_client:
                return await self._check_redis_limit(key, current_time, window_start, limits)
            else:
                return self._check_memory_limit(key, current_time, window_start, limits)
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Fail open - allow request but log error
            return True, {"remaining": 999, "reset": current_time + 3600}
    
    async def _check_redis_limit(self, key: str, current_time: int, window_start: int, limits: Dict) -> Tuple[bool, Dict]:
        """Check rate limit using Redis."""
        pipe = self.redis_client.pipeline()
        
        # Remove old entries and count current requests
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(current_time): current_time})
        pipe.expire(key, limits["window"])
        
        results = pipe.execute()
        request_count = results[1]
        
        # Calculate remaining and reset time
        remaining = max(0, limits["requests"] - request_count)
        reset_time = current_time + limits["window"]
        
        rate_info = {
            "remaining": remaining,
            "reset": reset_time,
            "limit": limits["requests"],
            "window": limits["window"]
        }
        
        # Check if limit exceeded
        allowed = request_count < limits["requests"]
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for key {key}: {request_count}/{limits['requests']}")
        
        return allowed, rate_info
    
    def _check_memory_limit(self, key: str, current_time: int, window_start: int, limits: Dict) -> Tuple[bool, Dict]:
        """Check rate limit using in-memory storage."""
        if key not in self.memory_store:
            self.memory_store[key] = {"requests": [], "created": current_time}
        
        # Remove old requests
        store = self.memory_store[key]
        store["requests"] = [req_time for req_time in store["requests"] if req_time > window_start]
        
        # Add current request
        store["requests"].append(current_time)
        request_count = len(store["requests"])
        
        # Calculate remaining and reset time
        remaining = max(0, limits["requests"] - request_count)
        reset_time = current_time + limits["window"]
        
        rate_info = {
            "remaining": remaining,
            "reset": reset_time,
            "limit": limits["requests"],
            "window": limits["window"]
        }
        
        # Check if limit exceeded
        allowed = request_count <= limits["requests"]
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for key {key}: {request_count}/{limits['requests']}")
        
        return allowed, rate_info

class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
        self.rate_limiter = RedisRateLimiter() if enabled else None
        if enabled:
            logger.info("Rate limiting middleware enabled")
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting if disabled or for health checks
        if not self.enabled or request.url.path in ["/health", "/readyz", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        try:
            allowed, rate_info = await self.rate_limiter.is_allowed(request)
            
            if not allowed:
                logger.warning(f"Rate limit exceeded for {request.client.host if request.client else 'unknown'} on {request.url.path}")
                
                response = HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Limit: {rate_info['limit']} per {rate_info['window']} seconds",
                        "retry_after": rate_info['reset'] - int(time.time())
                    }
                )
                
                # Add rate limit headers
                headers = {
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(rate_info["reset"]),
                    "Retry-After": str(rate_info['reset'] - int(time.time()))
                }
                
                response.headers = headers
                raise response
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers to successful responses
            response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Fail open - allow request
            return await call_next(request)