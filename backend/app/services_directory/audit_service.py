"""
Audit logging service for tracking critical actions and security events
Provides comprehensive audit trails for compliance and security monitoring
"""

import json
import asyncio
from typing import Any, Dict, Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from app.db.db import get_db, Base
import logging

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Enumeration of audit actions"""
    # Authentication actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    LOGIN_FAILED = "login_failed"
    TOKEN_REFRESH = "token_refresh"
    
    # User actions
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    PASSWORD_CHANGE = "password_change"
    PROFILE_UPDATE = "profile_update"
    
    # Business actions
    BUSINESS_CREATE = "business_create"
    BUSINESS_UPDATE = "business_update"
    BUSINESS_DELETE = "business_delete"
    BUSINESS_ACCESS = "business_access"
    
    # Product actions
    PRODUCT_CREATE = "product_create"
    PRODUCT_UPDATE = "product_update"
    PRODUCT_DELETE = "product_delete"
    PRICE_CHANGE = "price_change"
    
    # Order actions
    ORDER_CREATE = "order_create"
    ORDER_UPDATE = "order_update"
    ORDER_CANCEL = "order_cancel"
    ORDER_COMPLETE = "order_complete"
    
    # Payment actions
    PAYMENT_CREATE = "payment_create"
    PAYMENT_UPDATE = "payment_update"
    PAYMENT_WEBHOOK = "payment_webhook"
    PAYMENT_FAILED = "payment_failed"
    
    # Analytics actions
    ANALYTICS_ACCESS = "analytics_access"
    REPORT_GENERATE = "report_generate"
    DATA_EXPORT = "data_export"
    
    # Security actions
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_HIT = "rate_limit_hit"
    VALIDATION_ERROR = "validation_error"
    
    # Admin actions
    ADMIN_ACCESS = "admin_access"
    CONFIG_CHANGE = "config_change"
    USER_IMPERSONATE = "user_impersonate"


class AuditSeverity(str, Enum):
    """Audit log severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditLog(Base):
    """Audit log model for database storage"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Action details
    action = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    
    # User context
    user_id = Column(String, nullable=True, index=True)
    username = Column(String(100), nullable=True)
    user_role = Column(String(50), nullable=True)
    
    # Request context
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String, nullable=True, index=True)
    
    # Resource context
    resource_type = Column(String(50), nullable=True, index=True)
    resource_id = Column(String, nullable=True, index=True)
    business_id = Column(String, nullable=True, index=True)
    
    # Action details
    description = Column(Text, nullable=False)
    details = Column(Text, nullable=True)  # JSON string
    old_values = Column(Text, nullable=True)  # JSON string
    new_values = Column(Text, nullable=True)  # JSON string
    
    # Status
    success = Column(Boolean, default=True, nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    
    # Additional metadata
    session_id = Column(String, nullable=True, index=True)
    correlation_id = Column(String, nullable=True, index=True)


class AuditService:
    """Service for audit logging and retrieval"""
    
    def __init__(self):
        self.enabled = True
    
    async def log_action(
        self,
        action: AuditAction,
        description: str,
        user_id: Optional[UUID] = None,
        username: Optional[str] = None,
        user_role: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        business_id: Optional[UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        success: bool = True,
        error_message: Optional[str] = None,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> bool:
        """Log an audit action"""
        if not self.enabled:
            return True
        
        try:
            # Create audit log entry
            audit_log = AuditLog(
                action=action.value,
                severity=severity.value,
                user_id=str(user_id) if user_id else None,
                username=username,
                user_role=user_role,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else None,
                business_id=str(business_id) if business_id else None,
                description=description,
                details=json.dumps(details) if details else None,
                old_values=json.dumps(old_values) if old_values else None,
                new_values=json.dumps(new_values) if new_values else None,
                success=success,
                error_message=error_message,
                session_id=session_id,
                correlation_id=correlation_id
            )
            
            # Save to database
            if db is None:
                db = next(get_db())
            
            db.add(audit_log)
            db.commit()
            
            # Log to application logger for immediate visibility
            log_level = logging.WARNING if not success or severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL] else logging.INFO
            logger.log(
                log_level,
                f"AUDIT [{action.value}] {description} | User: {username} | IP: {ip_address} | Success: {success}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to log audit action: {e}")
            # Fallback to file logging
            try:
                self._log_to_file(action, description, user_id, ip_address, success, error_message)
            except Exception as file_error:
                logger.error(f"Failed to log to file: {file_error}")
            return False
    
    def _log_to_file(self, action: AuditAction, description: str, user_id: Optional[UUID], ip_address: Optional[str], success: bool, error_message: Optional[str]):
        """Fallback logging to file when database is unavailable"""
        import os
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action.value,
            "description": description,
            "user_id": str(user_id) if user_id else None,
            "ip_address": ip_address,
            "success": success,
            "error_message": error_message
        }
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        # Write to audit log file
        with open("logs/audit.log", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    async def get_audit_logs(
        self,
        db: Session,
        user_id: Optional[UUID] = None,
        business_id: Optional[UUID] = None,
        action: Optional[AuditAction] = None,
        severity: Optional[AuditSeverity] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        success: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Retrieve audit logs with filtering"""
        try:
            query = db.query(AuditLog)
            
            # Apply filters
            if user_id:
                query = query.filter(AuditLog.user_id == str(user_id))
            
            if business_id:
                query = query.filter(AuditLog.business_id == str(business_id))
            
            if action:
                query = query.filter(AuditLog.action == action.value)
            
            if severity:
                query = query.filter(AuditLog.severity == severity.value)
            
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)
            
            if success is not None:
                query = query.filter(AuditLog.success == success)
            
            # Order by timestamp (newest first)
            query = query.order_by(AuditLog.timestamp.desc())
            
            # Apply pagination
            return query.offset(offset).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Failed to retrieve audit logs: {e}")
            return []
    
    async def get_security_summary(self, db: Session, hours: int = 24) -> Dict[str, Any]:
        """Get security-related audit summary for the last N hours"""
        try:
            from datetime import timedelta
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Get security-related actions
            security_actions = [
                AuditAction.LOGIN_FAILED,
                AuditAction.PERMISSION_DENIED,
                AuditAction.SUSPICIOUS_ACTIVITY,
                AuditAction.RATE_LIMIT_HIT,
                AuditAction.VALIDATION_ERROR
            ]
            
            summary = {}
            
            for action in security_actions:
                count = db.query(AuditLog).filter(
                    AuditLog.action == action.value,
                    AuditLog.timestamp >= start_time
                ).count()
                summary[action.value] = count
            
            # Get failed actions
            failed_count = db.query(AuditLog).filter(
                AuditLog.success == False,
                AuditLog.timestamp >= start_time
            ).count()
            summary["total_failed_actions"] = failed_count
            
            # Get unique IP addresses with failed actions
            failed_ips = db.query(AuditLog.ip_address).filter(
                AuditLog.success == False,
                AuditLog.timestamp >= start_time,
                AuditLog.ip_address.isnot(None)
            ).distinct().count()
            summary["unique_failed_ips"] = failed_ips
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get security summary: {e}")
            return {}
    
    async def get_user_activity(self, db: Session, user_id: UUID, hours: int = 24) -> Dict[str, Any]:
        """Get user activity summary"""
        try:
            from datetime import timedelta
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            logs = db.query(AuditLog).filter(
                AuditLog.user_id == str(user_id),
                AuditLog.timestamp >= start_time
            ).order_by(AuditLog.timestamp.desc()).all()
            
            return {
                "total_actions": len(logs),
                "successful_actions": len([log for log in logs if log.success]),
                "failed_actions": len([log for log in logs if not log.success]),
                "unique_ips": len(set(log.ip_address for log in logs if log.ip_address)),
                "last_login": max([log.timestamp for log in logs if log.action == AuditAction.USER_LOGIN.value], default=None),
                "recent_actions": [
                    {
                        "action": log.action,
                        "timestamp": log.timestamp.isoformat(),
                        "success": log.success,
                        "description": log.description
                    }
                    for log in logs[:10]  # Last 10 actions
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get user activity: {e}")
            return {}


# Global audit service instance
audit_service = AuditService()


# Decorator for automatic audit logging
def audit_action(action: AuditAction, description: str = "", severity: AuditSeverity = AuditSeverity.MEDIUM):
    """Decorator for automatic audit logging of function calls"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            success = True
            error_message = None
            result = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                # Extract context from function arguments
                user_id = kwargs.get('current_user', {}).get('id') if isinstance(kwargs.get('current_user'), dict) else getattr(kwargs.get('current_user'), 'id', None)
                username = kwargs.get('current_user', {}).get('username') if isinstance(kwargs.get('current_user'), dict) else getattr(kwargs.get('current_user'), 'username', None)
                
                # Log the action
                await audit_service.log_action(
                    action=action,
                    description=description or f"{func.__name__} called",
                    user_id=user_id,
                    username=username,
                    success=success,
                    error_message=error_message,
                    severity=severity,
                    details={
                        "function": func.__name__,
                        "duration_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
                    }
                )
        
        return wrapper
    return decorator


# Utility functions for common audit scenarios
class AuditUtils:
    """Utility functions for common audit logging scenarios"""
    
    @staticmethod
    async def log_authentication(user_id: UUID, username: str, ip_address: str, success: bool, error_message: Optional[str] = None):
        """Log authentication attempt"""
        action = AuditAction.USER_LOGIN if success else AuditAction.LOGIN_FAILED
        severity = AuditSeverity.MEDIUM if success else AuditSeverity.HIGH
        
        await audit_service.log_action(
            action=action,
            description=f"Authentication {'successful' if success else 'failed'} for user {username}",
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            success=success,
            error_message=error_message,
            severity=severity
        )
    
    @staticmethod
    async def log_permission_denied(user_id: UUID, username: str, resource: str, ip_address: str):
        """Log permission denied event"""
        await audit_service.log_action(
            action=AuditAction.PERMISSION_DENIED,
            description=f"Permission denied for user {username} accessing {resource}",
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            success=False,
            severity=AuditSeverity.HIGH
        )
    
    @staticmethod
    async def log_data_change(action: AuditAction, user_id: UUID, username: str, resource_type: str, resource_id: UUID, old_values: Dict, new_values: Dict):
        """Log data modification"""
        await audit_service.log_action(
            action=action,
            description=f"{resource_type} {action.value.replace('_', ' ')} by {username}",
            user_id=user_id,
            username=username,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            severity=AuditSeverity.MEDIUM
        )


# Export audit utilities
audit_utils = AuditUtils()