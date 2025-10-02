"""
Rate Limiting Middleware
Protege endpoints contra ataques de fuerza bruta
"""
from fastapi import Request, HTTPException, status
from typing import Callable, Dict
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class InMemoryRateLimiter:
    """
    Rate limiter simple usando memoria
    Para producción, considerar Redis
    """
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
    
    def is_allowed(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Verificar si la solicitud está dentro del límite
        
        Args:
            key: Identificador único (ej: IP+endpoint)
            max_requests: Máximo de requests permitidos
            window_seconds: Ventana de tiempo en segundos
        
        Returns:
            (is_allowed, remaining_requests)
        """
        current_time = time.time()
        
        # Inicializar si no existe
        if key not in self.requests:
            self.requests[key] = []
        
        # Limpiar requests antiguos fuera de la ventana
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if current_time - req_time < window_seconds
        ]
        
        # Verificar si excede el límite
        current_count = len(self.requests[key])
        
        if current_count >= max_requests:
            return False, 0
        
        # Registrar request actual
        self.requests[key].append(current_time)
        remaining = max_requests - (current_count + 1)
        
        return True, remaining
    
    def clear(self):
        """Limpiar todos los registros (útil para testing)"""
        self.requests.clear()


# Instancia global del rate limiter
_rate_limiter = InMemoryRateLimiter()


def get_rate_limiter() -> InMemoryRateLimiter:
    """Obtener instancia del rate limiter"""
    return _rate_limiter


def rate_limit(max_requests: int = 5, window: int = 60):
    """
    Decorador para aplicar rate limiting a endpoints
    
    Args:
        max_requests: Máximo número de requests permitidos
        window: Ventana de tiempo en segundos
    
    Uso:
        @router.post("/login")
        @rate_limit(max_requests=5, window=60)
        async def login(request: Request, ...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Buscar el objeto Request en los argumentos
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            # Si no hay Request, permitir (útil para testing)
            if not request:
                return await func(*args, **kwargs)
            
            # Crear clave única: IP + endpoint
            client_ip = request.client.host if request.client else "unknown"
            endpoint = request.url.path
            rate_limit_key = f"{client_ip}:{endpoint}"
            
            # Verificar rate limit
            limiter = get_rate_limiter()
            is_allowed, remaining = limiter.is_allowed(
                rate_limit_key, 
                max_requests, 
                window
            )
            
            if not is_allowed:
                # Loguear intento bloqueado
                logger.warning(
                    f"Rate limit exceeded: {client_ip} on {endpoint}",
                    extra={
                        "ip": client_ip,
                        "endpoint": endpoint,
                        "user_agent": request.headers.get("user-agent", "unknown"),
                        "timestamp": time.time()
                    }
                )
                
                # Retornar error 429
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Too many requests",
                        "message": f"Rate limit exceeded. Try again in {window} seconds.",
                        "retry_after": window
                    },
                    headers={"Retry-After": str(window)}
                )
            
            # Ejecutar función original
            response = await func(*args, **kwargs)
            
            # Agregar headers informativos
            if hasattr(response, 'headers'):
                response.headers["X-RateLimit-Limit"] = str(max_requests)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
                response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
            
            return response
        
        return wrapper
    return decorator
