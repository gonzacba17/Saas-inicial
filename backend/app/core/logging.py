"""
Enhanced logging configuration for SaaS Cafeterías
Provides structured logging with JSON format, correlation IDs, and metrics integration
"""

import logging
import logging.config
import json
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar
import traceback
from pathlib import Path

# Context variables for request tracing
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)

class StructuredJSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'service': 'saas-backend',
            'environment': getattr(record, 'environment', 'production'),
        }
        
        # Add request context if available
        request_id = request_id_var.get()
        if request_id:
            log_obj['request_id'] = request_id
            
        user_id = user_id_var.get()
        if user_id:
            log_obj['user_id'] = user_id
            
        # Add custom fields
        if hasattr(record, 'custom_fields'):
            log_obj.update(record.custom_fields)
            
        # Add exception information
        if record.exc_info:
            log_obj['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
            
        # Add extra fields from LoggerAdapter
        extra_fields = ['user_id', 'business_id', 'order_id', 'amount', 'endpoint', 
                       'method', 'status_code', 'response_time_ms', 'event_type']
        for field in extra_fields:
            if hasattr(record, field):
                log_obj[field] = getattr(record, field)
                
        return json.dumps(log_obj, default=str)

class BusinessMetricsLogger:
    """Logger for business metrics and events"""
    
    def __init__(self, logger_name: str = "business_metrics"):
        self.logger = logging.getLogger(logger_name)
        
    def log_order_created(self, order_id: str, business_id: str, amount: float, 
                         user_id: str = None):
        """Log order creation event"""
        self.logger.info(
            "Order created successfully",
            extra={
                'event_type': 'order_created',
                'order_id': order_id,
                'business_id': business_id,
                'amount': amount,
                'user_id': user_id
            }
        )
        
    def log_payment_processed(self, order_id: str, amount: float, payment_method: str,
                             status: str = 'success'):
        """Log payment processing event"""
        self.logger.info(
            f"Payment {status}",
            extra={
                'event_type': 'payment_processed',
                'order_id': order_id,
                'amount': amount,
                'payment_method': payment_method,
                'payment_status': status
            }
        )
        
    def log_user_registered(self, user_id: str, business_id: str = None):
        """Log user registration event"""
        self.logger.info(
            "New user registered",
            extra={
                'event_type': 'user_registered',
                'user_id': user_id,
                'business_id': business_id
            }
        )
        
    def log_business_created(self, business_id: str, user_id: str, plan: str):
        """Log business creation event"""
        self.logger.info(
            "New business created",
            extra={
                'event_type': 'business_created',
                'business_id': business_id,
                'user_id': user_id,
                'plan': plan
            }
        )

class SecurityLogger:
    """Logger for security events"""
    
    def __init__(self, logger_name: str = "security"):
        self.logger = logging.getLogger(logger_name)
        
    def log_auth_failure(self, username: str, ip_address: str, reason: str = None):
        """Log authentication failure"""
        self.logger.warning(
            f"Authentication failed for user: {username}",
            extra={
                'event_type': 'auth_failure',
                'username': username,
                'source_ip': ip_address,
                'failure_reason': reason,
                'alert_type': 'auth_failure'
            }
        )
        
    def log_suspicious_activity(self, user_id: str, activity: str, ip_address: str,
                               details: Dict = None):
        """Log suspicious security activity"""
        self.logger.error(
            f"Suspicious activity detected: {activity}",
            extra={
                'event_type': 'suspicious_activity',
                'user_id': user_id,
                'activity': activity,
                'source_ip': ip_address,
                'details': details or {},
                'alert_type': 'security_threat',
                'severity': 'high'
            }
        )
        
    def log_rate_limit_exceeded(self, endpoint: str, ip_address: str, limit: int):
        """Log rate limit violations"""
        self.logger.warning(
            f"Rate limit exceeded for endpoint: {endpoint}",
            extra={
                'event_type': 'rate_limit_exceeded',
                'endpoint': endpoint,
                'source_ip': ip_address,
                'rate_limit': limit
            }
        )

class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = logging.getLogger(logger_name)
        
    def log_slow_query(self, query: str, duration_ms: int, table: str = None):
        """Log slow database queries"""
        self.logger.warning(
            f"Slow query detected: {duration_ms}ms",
            extra={
                'event_type': 'slow_query',
                'query': query[:500],  # Truncate long queries
                'duration_ms': duration_ms,
                'table': table
            }
        )
        
    def log_api_response(self, endpoint: str, method: str, status_code: int,
                        response_time_ms: int, user_id: str = None):
        """Log API response metrics"""
        level = logging.INFO
        if response_time_ms > 2000:  # Slow response
            level = logging.WARNING
        elif status_code >= 500:  # Server error
            level = logging.ERROR
            
        self.logger.log(
            level,
            f"API response: {method} {endpoint} - {status_code}",
            extra={
                'event_type': 'api_response',
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code,
                'response_time_ms': response_time_ms,
                'user_id': user_id
            }
        )

def setup_logging(log_level: str = "INFO", log_file: str = None) -> None:
    """Setup structured logging configuration"""
    
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': StructuredJSONFormatter,
            },
            'simple': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'json',
                'stream': sys.stdout,
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': log_level,
                'formatter': 'json',
                'filename': log_file or 'logs/app.log',
                'maxBytes': 50 * 1024 * 1024,  # 50MB
                'backupCount': 10,
            },
            'business_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'json',
                'filename': 'logs/business.log',
                'maxBytes': 50 * 1024 * 1024,
                'backupCount': 5,
            },
            'security_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'WARNING',
                'formatter': 'json',
                'filename': 'logs/security.log',
                'maxBytes': 50 * 1024 * 1024,
                'backupCount': 10,
            },
            'performance_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'json',
                'filename': 'logs/performance.log',
                'maxBytes': 50 * 1024 * 1024,
                'backupCount': 5,
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False,
            },
            'business_metrics': {
                'handlers': ['business_file', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
            'security': {
                'handlers': ['security_file', 'console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'performance': {
                'handlers': ['performance_file', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
            # External libraries
            'uvicorn': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
            'sqlalchemy': {
                'handlers': ['file'],
                'level': 'WARNING',
                'propagate': False,
            }
        }
    }
    
    logging.config.dictConfig(config)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)

def set_request_context(request_id: str = None, user_id: str = None):
    """Set request context for correlation"""
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    return request_id

def clear_request_context():
    """Clear request context"""
    request_id_var.set(None)
    user_id_var.set(None)

# Initialize specialized loggers
business_logger = BusinessMetricsLogger()
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()