"""
Cache Service for Redis integration with fallback to in-memory cache
Provides high-performance caching for frequent database queries
"""

import json
import redis
import asyncio
from typing import Any, Optional, Union, Dict
from functools import wraps
from datetime import timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis cache service with fallback to in-memory cache"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache: Dict[str, Any] = {}
        self.memory_cache_ttl: Dict[str, float] = {}
        self._connect_redis()
    
    def _connect_redis(self):
        """Connect to Redis with fallback to memory cache"""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("✓ Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed, using memory cache: {e}")
            self.redis_client = None
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for storage"""
        return json.dumps(value, default=str, ensure_ascii=False)
    
    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from storage"""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis_client:
                # Redis cache
                value = await asyncio.to_thread(self.redis_client.get, key)
                if value:
                    return self._deserialize_value(value)
            else:
                # Memory cache fallback
                import time
                if key in self.memory_cache:
                    # Check TTL
                    if key in self.memory_cache_ttl:
                        if time.time() > self.memory_cache_ttl[key]:
                            # Expired
                            del self.memory_cache[key]
                            del self.memory_cache_ttl[key]
                            return None
                    return self.memory_cache[key]
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        try:
            ttl = ttl or settings.cache_default_ttl
            serialized_value = self._serialize_value(value)
            
            if self.redis_client:
                # Redis cache
                return await asyncio.to_thread(
                    self.redis_client.setex, 
                    key, 
                    ttl, 
                    serialized_value
                )
            else:
                # Memory cache fallback
                import time
                self.memory_cache[key] = value
                self.memory_cache_ttl[key] = time.time() + ttl
                return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.redis_client:
                # Redis cache
                return await asyncio.to_thread(self.redis_client.delete, key) > 0
            else:
                # Memory cache fallback
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    if key in self.memory_cache_ttl:
                        del self.memory_cache_ttl[key]
                    return True
                return False
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            if self.redis_client:
                # Redis cache
                keys = await asyncio.to_thread(self.redis_client.keys, pattern)
                if keys:
                    return await asyncio.to_thread(self.redis_client.delete, *keys)
                return 0
            else:
                # Memory cache fallback
                import fnmatch
                keys_to_delete = [
                    key for key in self.memory_cache.keys() 
                    if fnmatch.fnmatch(key, pattern)
                ]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                    if key in self.memory_cache_ttl:
                        del self.memory_cache_ttl[key]
                return len(keys_to_delete)
        except Exception as e:
            logger.error(f"Cache clear pattern error for pattern {pattern}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if self.redis_client:
                return await asyncio.to_thread(self.redis_client.exists, key) > 0
            else:
                import time
                if key in self.memory_cache:
                    # Check TTL
                    if key in self.memory_cache_ttl:
                        if time.time() > self.memory_cache_ttl[key]:
                            del self.memory_cache[key]
                            del self.memory_cache_ttl[key]
                            return False
                    return True
                return False
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment numeric value in cache"""
        try:
            if self.redis_client:
                return await asyncio.to_thread(self.redis_client.incr, key, amount)
            else:
                current = self.memory_cache.get(key, 0)
                new_value = int(current) + amount
                self.memory_cache[key] = new_value
                return new_value
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if self.redis_client:
                info = await asyncio.to_thread(self.redis_client.info, "memory")
                return {
                    "type": "redis",
                    "connected": True,
                    "memory_used": info.get("used_memory_human", "unknown"),
                    "keys": await asyncio.to_thread(self.redis_client.dbsize)
                }
            else:
                return {
                    "type": "memory",
                    "connected": False,
                    "keys": len(self.memory_cache),
                    "memory_keys": list(self.memory_cache.keys())[:10]  # First 10 keys
                }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"type": "unknown", "connected": False, "error": str(e)}


# Global cache instance
cache = CacheService()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_parts = []
    
    # Add positional arguments
    for arg in args:
        if hasattr(arg, 'id'):
            key_parts.append(f"{type(arg).__name__}:{arg.id}")
        else:
            key_parts.append(str(arg))
    
    # Add keyword arguments
    for k, v in sorted(kwargs.items()):
        if hasattr(v, 'id'):
            key_parts.append(f"{k}:{type(v).__name__}:{v.id}")
        else:
            key_parts.append(f"{k}:{v}")
    
    return ":".join(key_parts)


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator for caching function results
    
    Usage:
    @cached(ttl=300, key_prefix="user")
    async def get_user_by_id(user_id: int):
        # This result will be cached for 5 minutes
        return await db.get_user(user_id)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            func_name = f"{func.__module__}.{func.__name__}"
            key = f"{key_prefix}:{func_name}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = await cache.get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {key}")
                return cached_result
            
            # Execute function
            logger.debug(f"Cache miss for key: {key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            if result is not None:
                await cache.set(key, result, ttl)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Decorator for invalidating cache patterns after function execution
    
    Usage:
    @invalidate_cache("user:*")
    async def update_user(user_id: int, data: dict):
        # After this function, all user:* cache keys will be cleared
        return await db.update_user(user_id, data)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            # Clear cache pattern after successful execution
            cleared = await cache.clear_pattern(pattern)
            logger.debug(f"Cleared {cleared} cache keys matching pattern: {pattern}")
            return result
        return wrapper
    return decorator


# Cache utility functions for common patterns
class CacheUtils:
    """Utility functions for common caching patterns"""
    
    @staticmethod
    async def cache_business_data(business_id: int, data: Any, ttl: int = None):
        """Cache business-related data"""
        key = f"business:{business_id}:data"
        return await cache.set(key, data, ttl or settings.cache_long_ttl)
    
    @staticmethod
    async def get_cached_business_data(business_id: int) -> Optional[Any]:
        """Get cached business data"""
        key = f"business:{business_id}:data"
        return await cache.get(key)
    
    @staticmethod
    async def cache_user_session(user_id: int, session_data: Any):
        """Cache user session data"""
        key = f"session:user:{user_id}"
        return await cache.set(key, session_data, settings.cache_short_ttl)
    
    @staticmethod
    async def invalidate_user_cache(user_id: int):
        """Invalidate all user-related cache"""
        pattern = f"*user:{user_id}*"
        return await cache.clear_pattern(pattern)
    
    @staticmethod
    async def cache_analytics_data(business_id: int, period: str, data: Any):
        """Cache analytics data with longer TTL"""
        key = f"analytics:business:{business_id}:period:{period}"
        return await cache.set(key, data, settings.cache_long_ttl)
    
    @staticmethod
    async def get_cached_analytics(business_id: int, period: str) -> Optional[Any]:
        """Get cached analytics data"""
        key = f"analytics:business:{business_id}:period:{period}"
        return await cache.get(key)


# Export cache utilities
cache_utils = CacheUtils()