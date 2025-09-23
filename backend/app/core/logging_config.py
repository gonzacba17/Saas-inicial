"""
Centralized logging configuration with structured logging and alerting.
Provides comprehensive logging for security events, performance monitoring, and error tracking.
"""
import logging
import logging.handlers
import json
import os
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class LogLevel(Enum):
    """Log levels for categorizing messages."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SecurityEventType(Enum):
    """Security event types for monitoring."""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    FORBIDDEN_ACCESS = "forbidden_access"
    TOKEN_VALIDATION_ERROR = "token_validation_error"
    ADMIN_ACTION = "admin_action"
    DATA_ACCESS = "data_access"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address
        if hasattr(record, 'user_agent'):
            log_entry['user_agent'] = record.user_agent
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'method'):
            log_entry['method'] = record.method
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        if hasattr(record, 'response_time'):
            log_entry['response_time'] = record.response_time
        if hasattr(record, 'security_event'):
            log_entry['security_event'] = record.security_event
        if hasattr(record, 'business_id'):
            log_entry['business_id'] = record.business_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            log_entry['stack_trace'] = traceback.format_exception(*record.exc_info)
        
        return json.dumps(log_entry)


class CentralizedLogger:
    """Centralized logging system with security event tracking."""
    
    def __init__(self):
        self.setup_logging()
        self.security_logger = logging.getLogger('security')
        self.performance_logger = logging.getLogger('performance')
        self.business_logger = logging.getLogger('business')
        
    def setup_logging(self):
        """Setup centralized logging configuration."""
        # Create logs directory if it doesn't exist
        logs_dir = '/mnt/c/wamp64/www/Saas-inicial/logs'
        os.makedirs(logs_dir, exist_ok=True)
        
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler for general application logs
        file_handler = logging.handlers.RotatingFileHandler(
            filename=f'{logs_dir}/app.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(StructuredFormatter())
        
        # Security events handler
        security_handler = logging.handlers.RotatingFileHandler(
            filename=f'{logs_dir}/security.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10  # Keep more security logs
        )
        security_handler.setLevel(logging.INFO)
        security_handler.setFormatter(StructuredFormatter())
        
        # Performance handler
        performance_handler = logging.handlers.RotatingFileHandler(
            filename=f'{logs_dir}/performance.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        performance_handler.setLevel(logging.INFO)
        performance_handler.setFormatter(StructuredFormatter())
        
        # Error handler for critical issues
        error_handler = logging.handlers.RotatingFileHandler(
            filename=f'{logs_dir}/errors.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        
        # Add handlers to root logger
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(error_handler)
        
        # Setup specialized loggers
        security_logger = logging.getLogger('security')
        security_logger.addHandler(security_handler)
        security_logger.propagate = False
        
        performance_logger = logging.getLogger('performance')
        performance_logger.addHandler(performance_handler)
        performance_logger.propagate = False
        
        business_logger = logging.getLogger('business')
        business_logger.addHandler(file_handler)
        business_logger.propagate = False
    
    def log_security_event(self, 
                          event_type: SecurityEventType, 
                          message: str,
                          user_id: Optional[str] = None,
                          ip_address: Optional[str] = None,
                          user_agent: Optional[str] = None,
                          endpoint: Optional[str] = None,
                          additional_data: Optional[Dict[str, Any]] = None):
        """Log security-related events with structured data."""
        extra = {
            'security_event': event_type.value,
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'endpoint': endpoint,
        }
        
        if additional_data:
            extra.update(additional_data)
        
        # Filter out None values
        extra = {k: v for k, v in extra.items() if v is not None}
        
        # Log at appropriate level based on event type
        if event_type in [SecurityEventType.UNAUTHORIZED_ACCESS, 
                         SecurityEventType.FORBIDDEN_ACCESS,
                         SecurityEventType.TOKEN_VALIDATION_ERROR]:
            self.security_logger.warning(message, extra=extra)
        elif event_type == SecurityEventType.LOGIN_FAILURE:
            self.security_logger.warning(message, extra=extra)
        else:
            self.security_logger.info(message, extra=extra)
    
    def log_performance_event(self,
                            endpoint: str,
                            method: str,
                            response_time: float,
                            status_code: int,
                            user_id: Optional[str] = None,
                            additional_data: Optional[Dict[str, Any]] = None):
        """Log performance metrics for endpoints."""
        extra = {
            'endpoint': endpoint,
            'method': method,
            'response_time': response_time,
            'status_code': status_code,
            'user_id': user_id,
        }
        
        if additional_data:
            extra.update(additional_data)
        
        # Filter out None values
        extra = {k: v for k, v in extra.items() if v is not None}
        
        # Log warning for slow endpoints
        if response_time > 1000:  # > 1 second
            self.performance_logger.warning(
                f"Slow endpoint: {method} {endpoint} took {response_time}ms",
                extra=extra
            )
        else:
            self.performance_logger.info(
                f"Performance: {method} {endpoint} - {response_time}ms",
                extra=extra
            )
    
    def log_business_event(self,
                          event: str,
                          message: str,
                          user_id: Optional[str] = None,
                          business_id: Optional[str] = None,
                          additional_data: Optional[Dict[str, Any]] = None):
        """Log business-related events."""
        extra = {
            'business_event': event,
            'user_id': user_id,
            'business_id': business_id,
        }
        
        if additional_data:
            extra.update(additional_data)
        
        # Filter out None values
        extra = {k: v for k, v in extra.items() if v is not None}
        
        self.business_logger.info(message, extra=extra)
    
    def log_error(self,
                  message: str,
                  exception: Optional[Exception] = None,
                  user_id: Optional[str] = None,
                  endpoint: Optional[str] = None,
                  additional_data: Optional[Dict[str, Any]] = None):
        """Log error events with full context."""
        extra = {
            'user_id': user_id,
            'endpoint': endpoint,
        }
        
        if additional_data:
            extra.update(additional_data)
        
        # Filter out None values
        extra = {k: v for k, v in extra.items() if v is not None}
        
        if exception:
            logging.error(message, exc_info=exception, extra=extra)
        else:
            logging.error(message, extra=extra)


class AlertManager:
    """Manages alerts for critical events."""
    
    def __init__(self):
        self.alert_thresholds = {
            'failed_logins_per_minute': 10,
            'error_rate_per_minute': 50,
            'slow_requests_per_minute': 20,
            'unauthorized_access_per_minute': 5,
        }
        self.alert_counts = {}
        self.last_reset = datetime.utcnow()
    
    def check_alert_thresholds(self, event_type: str):
        """Check if alert thresholds are exceeded."""
        now = datetime.utcnow()
        
        # Reset counters every minute
        if (now - self.last_reset).seconds >= 60:
            self.alert_counts = {}
            self.last_reset = now
        
        # Increment counter
        self.alert_counts[event_type] = self.alert_counts.get(event_type, 0) + 1
        
        # Check threshold
        threshold = self.alert_thresholds.get(event_type, float('inf'))
        if self.alert_counts[event_type] >= threshold:
            self.send_alert(event_type, self.alert_counts[event_type])
    
    def send_alert(self, event_type: str, count: int):
        """Send alert for critical events."""
        alert_message = f"ALERT: {event_type} threshold exceeded - {count} events in the last minute"
        
        # Log the alert
        logging.critical(alert_message, extra={
            'alert_type': event_type,
            'event_count': count,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # In production, you would send this to monitoring systems
        # like Slack, email, PagerDuty, etc.
        print(f"🚨 {alert_message}")


# Global instances
centralized_logger = CentralizedLogger()
alert_manager = AlertManager()


def log_security_event(event_type: SecurityEventType, message: str, **kwargs):
    """Convenience function for logging security events."""
    centralized_logger.log_security_event(event_type, message, **kwargs)
    
    # Check for alerts on critical security events
    if event_type in [SecurityEventType.LOGIN_FAILURE, 
                     SecurityEventType.UNAUTHORIZED_ACCESS,
                     SecurityEventType.FORBIDDEN_ACCESS]:
        alert_manager.check_alert_thresholds(event_type.value)


def log_performance_event(endpoint: str, method: str, response_time: float, 
                         status_code: int, **kwargs):
    """Convenience function for logging performance events."""
    centralized_logger.log_performance_event(endpoint, method, response_time, 
                                            status_code, **kwargs)
    
    # Check for slow request alerts
    if response_time > 1000:
        alert_manager.check_alert_thresholds('slow_requests_per_minute')


def log_business_event(event: str, message: str, **kwargs):
    """Convenience function for logging business events."""
    centralized_logger.log_business_event(event, message, **kwargs)


def log_error(message: str, exception: Optional[Exception] = None, **kwargs):
    """Convenience function for logging errors."""
    centralized_logger.log_error(message, exception, **kwargs)
    
    # Check for error rate alerts
    alert_manager.check_alert_thresholds('error_rate_per_minute')