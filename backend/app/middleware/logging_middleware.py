"""
Logging middleware for automatic request/response logging and monitoring.
Integrates with centralized logging system for comprehensive observability.
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import (
    log_security_event, 
    log_performance_event, 
    log_error,
    SecurityEventType
)
import logging


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request/response logging."""
    
    def __init__(self, app, log_requests: bool = True, log_responses: bool = True):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.logger = logging.getLogger('request_middleware')
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Extract request information
        start_time = time.time()
        method = request.method
        url = str(request.url)
        path = request.url.path
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        user_id = None
        
        # Extract user ID from authorization header if present
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                # You could decode the JWT token here to get user_id
                # For now, we'll extract it from the request state if available
                user_id = getattr(request.state, 'user_id', None)
            except Exception:
                pass
        
        # Log incoming request
        if self.log_requests:
            self.logger.info(
                f"Request: {method} {path}",
                extra={
                    'request_id': request_id,
                    'method': method,
                    'path': path,
                    'url': url,
                    'ip_address': client_ip,
                    'user_agent': user_agent,
                    'user_id': user_id,
                }
            )
        
        # Process request and measure time
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response_time_ms = process_time * 1000
            
            # Log response
            if self.log_responses:
                self.logger.info(
                    f"Response: {method} {path} - {response.status_code} ({response_time_ms:.2f}ms)",
                    extra={
                        'request_id': request_id,
                        'method': method,
                        'path': path,
                        'status_code': response.status_code,
                        'response_time': response_time_ms,
                        'ip_address': client_ip,
                        'user_id': user_id,
                    }
                )
            
            # Log performance metrics
            log_performance_event(
                endpoint=path,
                method=method,
                response_time=response_time_ms,
                status_code=response.status_code,
                user_id=user_id,
                additional_data={
                    'request_id': request_id,
                    'ip_address': client_ip,
                }
            )
            
            # Log security events based on status codes
            self._log_security_events(path, method, response.status_code, user_id, client_ip, user_agent)
            
            # Add headers for monitoring
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{response_time_ms:.2f}ms"
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            response_time_ms = process_time * 1000
            
            # Log error
            log_error(
                f"Request failed: {method} {path}",
                exception=e,
                user_id=user_id,
                endpoint=path,
                additional_data={
                    'request_id': request_id,
                    'method': method,
                    'ip_address': client_ip,
                    'user_agent': user_agent,
                    'response_time': response_time_ms,
                }
            )
            
            # Re-raise the exception
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers first (proxy/load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _log_security_events(self, path: str, method: str, status_code: int, 
                           user_id: str, ip_address: str, user_agent: str):
        """Log security-related events based on response status codes."""
        
        # Authentication/Authorization events
        if status_code == 401:
            if "/auth/login" in path:
                log_security_event(
                    SecurityEventType.LOGIN_FAILURE,
                    f"Failed login attempt from {ip_address}",
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    endpoint=path
                )
            else:
                log_security_event(
                    SecurityEventType.UNAUTHORIZED_ACCESS,
                    f"Unauthorized access attempt to {method} {path}",
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    endpoint=path
                )
        
        elif status_code == 403:
            log_security_event(
                SecurityEventType.FORBIDDEN_ACCESS,
                f"Forbidden access attempt to {method} {path}",
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=path
            )
        
        elif status_code == 200 and "/auth/login" in path:
            log_security_event(
                SecurityEventType.LOGIN_SUCCESS,
                f"Successful login from {ip_address}",
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=path
            )
        
        # Admin actions
        elif status_code in [200, 201] and user_id and self._is_admin_endpoint(path):
            log_security_event(
                SecurityEventType.ADMIN_ACTION,
                f"Admin action: {method} {path}",
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=path
            )
        
        # Data access
        elif status_code == 200 and method == "GET" and self._is_data_endpoint(path):
            log_security_event(
                SecurityEventType.DATA_ACCESS,
                f"Data access: {method} {path}",
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=path
            )
    
    def _is_admin_endpoint(self, path: str) -> bool:
        """Check if the endpoint requires admin privileges."""
        admin_endpoints = [
            "/api/v1/users/",  # List users
            "/api/v1/admin/",  # Admin endpoints
        ]
        
        # Check if path starts with any admin endpoint
        return any(path.startswith(endpoint) for endpoint in admin_endpoints)
    
    def _is_data_endpoint(self, path: str) -> bool:
        """Check if the endpoint accesses sensitive data."""
        data_endpoints = [
            "/api/v1/businesses",
            "/api/v1/products",
            "/api/v1/orders",
            "/api/v1/analytics",
            "/api/v1/users",
        ]
        
        # Check if path contains any data endpoint
        return any(endpoint in path for endpoint in data_endpoints)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Additional security middleware for monitoring suspicious activities."""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_counts = {}  # Simple in-memory rate limiting (use Redis in production)
        self.suspicious_patterns = [
            "admin",
            "root", 
            "administrator",
            "config",
            "database",
            "backup",
            "test",
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self._get_client_ip(request)
        path = request.url.path.lower()
        
        # Check for suspicious patterns in URL
        if any(pattern in path for pattern in self.suspicious_patterns):
            log_security_event(
                SecurityEventType.UNAUTHORIZED_ACCESS,
                f"Suspicious URL pattern detected: {path}",
                ip_address=client_ip,
                endpoint=path,
                additional_data={'pattern_match': True}
            )
        
        # Simple rate limiting check (basic implementation)
        current_time = time.time()
        minute_key = f"{client_ip}:{int(current_time // 60)}"
        
        if minute_key not in self.request_counts:
            self.request_counts[minute_key] = 0
        
        self.request_counts[minute_key] += 1
        
        # Clean old entries (simple cleanup)
        old_keys = [k for k in self.request_counts.keys() 
                   if int(k.split(':')[1]) < int(current_time // 60) - 5]
        for key in old_keys:
            del self.request_counts[key]
        
        # Check rate limit (100 requests per minute per IP)
        if self.request_counts[minute_key] > 100:
            log_security_event(
                SecurityEventType.RATE_LIMIT_EXCEEDED,
                f"Rate limit exceeded for IP {client_ip}",
                ip_address=client_ip,
                additional_data={'requests_per_minute': self.request_counts[minute_key]}
            )
        
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"