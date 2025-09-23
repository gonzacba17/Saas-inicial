"""
Secrets Management API endpoints
Provides secure access to secrets management functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.db.db import get_db, UserRole
from app.schemas import User as UserSchema
from app.api.v1.auth import get_current_user
from app.services_directory.secrets_service import secrets_manager
from app.services_directory.audit_service import audit_service, AuditAction, AuditSeverity
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic models for secrets API
class SecretCreate(BaseModel):
    name: str
    value: Dict[str, Any]


class SecretUpdate(BaseModel):
    value: Dict[str, Any]


class SecretResponse(BaseModel):
    name: str
    keys: List[str]  # Only return key names, not values
    created_at: Optional[str] = None
    backend: str


class SecretValue(BaseModel):
    name: str
    key: str
    value: Any


class SecretsBackupResponse(BaseModel):
    backup_id: str
    secret_count: int
    created_at: str


def check_admin_permission(current_user: UserSchema):
    """Check if user has admin permissions for secrets management"""
    if not hasattr(current_user, 'role') or current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required for secrets management"
        )


@router.get("/", response_model=List[str])
async def list_secrets(
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all available secrets (admin only)"""
    check_admin_permission(current_user)
    
    try:
        secrets = await secrets_manager.list_secrets()
        
        # Audit log
        await audit_service.log_action(
            action=AuditAction.ADMIN_ACCESS,
            description=f"Admin {current_user.username} listed secrets",
            user_id=current_user.id,
            username=current_user.username,
            severity=AuditSeverity.MEDIUM,
            success=True,
            db=db
        )
        
        return secrets
    except Exception as e:
        logger.error(f"Error listing secrets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list secrets"
        )


@router.get("/{secret_name}", response_model=SecretResponse)
async def get_secret_info(
    secret_name: str,
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get secret information without exposing values (admin only)"""
    check_admin_permission(current_user)
    
    try:
        secret = await secrets_manager.get_secret(secret_name)
        if not secret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Secret {secret_name} not found"
            )
        
        # Audit log
        await audit_service.log_action(
            action=AuditAction.ADMIN_ACCESS,
            description=f"Admin {current_user.username} accessed secret info: {secret_name}",
            user_id=current_user.id,
            username=current_user.username,
            resource_type="secret",
            resource_id=secret_name,
            severity=AuditSeverity.MEDIUM,
            success=True,
            db=db
        )
        
        return SecretResponse(
            name=secret_name,
            keys=list(secret.keys()),
            backend=type(secrets_manager.backend).__name__
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting secret info {secret_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get secret information"
        )


@router.get("/{secret_name}/{key}")
async def get_secret_value(
    secret_name: str,
    key: str,
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific secret value (admin only)"""
    check_admin_permission(current_user)
    
    try:
        value = await secrets_manager.get_secret_value(secret_name, key)
        if value is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Secret {secret_name} or key {key} not found"
            )
        
        # Audit log - don't log the actual value
        await audit_service.log_action(
            action=AuditAction.ADMIN_ACCESS,
            description=f"Admin {current_user.username} accessed secret value: {secret_name}.{key}",
            user_id=current_user.id,
            username=current_user.username,
            resource_type="secret",
            resource_id=f"{secret_name}.{key}",
            severity=AuditSeverity.HIGH,  # Higher severity for value access
            success=True,
            db=db
        )
        
        return SecretValue(name=secret_name, key=key, value=value)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting secret value {secret_name}.{key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get secret value"
        )


@router.post("/{secret_name}", status_code=status.HTTP_201_CREATED)
async def create_secret(
    secret_name: str,
    secret_data: SecretCreate,
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new secret (admin only)"""
    check_admin_permission(current_user)
    
    try:
        # Check if secret already exists
        existing = await secrets_manager.get_secret(secret_name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Secret {secret_name} already exists"
            )
        
        success = await secrets_manager.set_secret(secret_name, secret_data.value)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create secret"
            )
        
        # Audit log
        await audit_service.log_action(
            action=AuditAction.CONFIG_CHANGE,
            description=f"Admin {current_user.username} created secret: {secret_name}",
            user_id=current_user.id,
            username=current_user.username,
            resource_type="secret",
            resource_id=secret_name,
            new_values={"keys": list(secret_data.value.keys())},  # Don't log values
            severity=AuditSeverity.HIGH,
            success=True,
            db=db
        )
        
        return {"message": f"Secret {secret_name} created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating secret {secret_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create secret"
        )


@router.put("/{secret_name}")
async def update_secret(
    secret_name: str,
    secret_data: SecretUpdate,
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing secret (admin only)"""
    check_admin_permission(current_user)
    
    try:
        # Get old values for audit
        old_secret = await secrets_manager.get_secret(secret_name)
        if not old_secret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Secret {secret_name} not found"
            )
        
        success = await secrets_manager.set_secret(secret_name, secret_data.value)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update secret"
            )
        
        # Audit log
        await audit_service.log_action(
            action=AuditAction.CONFIG_CHANGE,
            description=f"Admin {current_user.username} updated secret: {secret_name}",
            user_id=current_user.id,
            username=current_user.username,
            resource_type="secret",
            resource_id=secret_name,
            old_values={"keys": list(old_secret.keys())},
            new_values={"keys": list(secret_data.value.keys())},
            severity=AuditSeverity.HIGH,
            success=True,
            db=db
        )
        
        return {"message": f"Secret {secret_name} updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating secret {secret_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update secret"
        )


@router.delete("/{secret_name}")
async def delete_secret(
    secret_name: str,
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a secret (admin only)"""
    check_admin_permission(current_user)
    
    try:
        # Get secret for audit before deletion
        old_secret = await secrets_manager.get_secret(secret_name)
        if not old_secret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Secret {secret_name} not found"
            )
        
        success = await secrets_manager.delete_secret(secret_name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete secret"
            )
        
        # Audit log
        await audit_service.log_action(
            action=AuditAction.CONFIG_CHANGE,
            description=f"Admin {current_user.username} deleted secret: {secret_name}",
            user_id=current_user.id,
            username=current_user.username,
            resource_type="secret",
            resource_id=secret_name,
            old_values={"keys": list(old_secret.keys())},
            severity=AuditSeverity.CRITICAL,  # Deletion is critical
            success=True,
            db=db
        )
        
        return {"message": f"Secret {secret_name} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting secret {secret_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete secret"
        )


@router.post("/{secret_name}/rotate")
async def rotate_secret(
    secret_name: str,
    secret_data: SecretUpdate,
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rotate a secret (admin only)"""
    check_admin_permission(current_user)
    
    try:
        # Get old values for audit
        old_secret = await secrets_manager.get_secret(secret_name)
        if not old_secret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Secret {secret_name} not found"
            )
        
        success = await secrets_manager.rotate_secret(secret_name, secret_data.value)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to rotate secret"
            )
        
        # Audit log
        await audit_service.log_action(
            action=AuditAction.CONFIG_CHANGE,
            description=f"Admin {current_user.username} rotated secret: {secret_name}",
            user_id=current_user.id,
            username=current_user.username,
            resource_type="secret",
            resource_id=secret_name,
            old_values={"keys": list(old_secret.keys())},
            new_values={"keys": list(secret_data.value.keys())},
            severity=AuditSeverity.HIGH,
            success=True,
            db=db
        )
        
        return {"message": f"Secret {secret_name} rotated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rotating secret {secret_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rotate secret"
        )


@router.post("/backup", response_model=SecretsBackupResponse)
async def backup_secrets(
    current_user: UserSchema = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a backup of all secrets (admin only)"""
    check_admin_permission(current_user)
    
    try:
        backup_data = await secrets_manager.backup_secrets()
        
        # Save backup with timestamp
        from datetime import datetime
        backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        backup_file = f"secrets_{backup_id}.json"
        
        import json
        import os
        os.makedirs("backups", exist_ok=True)
        
        with open(f"backups/{backup_file}", 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        # Audit log
        await audit_service.log_action(
            action=AuditAction.CONFIG_CHANGE,
            description=f"Admin {current_user.username} created secrets backup: {backup_id}",
            user_id=current_user.id,
            username=current_user.username,
            resource_type="backup",
            resource_id=backup_id,
            details={"secret_count": len(backup_data)},
            severity=AuditSeverity.MEDIUM,
            success=True,
            db=db
        )
        
        return SecretsBackupResponse(
            backup_id=backup_id,
            secret_count=len(backup_data),
            created_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Error creating secrets backup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create backup"
        )


@router.get("/status/health")
async def secrets_health_check(
    current_user: UserSchema = Depends(get_current_user)
):
    """Check secrets management system health (admin only)"""
    check_admin_permission(current_user)
    
    try:
        # Test basic operations
        test_secret_name = "health_check_test"
        test_data = {"test": "value", "timestamp": str(datetime.utcnow())}
        
        # Test create
        create_success = await secrets_manager.set_secret(test_secret_name, test_data)
        
        # Test read
        read_data = await secrets_manager.get_secret(test_secret_name)
        read_success = read_data is not None
        
        # Test delete
        delete_success = await secrets_manager.delete_secret(test_secret_name)
        
        # Test list
        secrets_list = await secrets_manager.list_secrets()
        list_success = isinstance(secrets_list, list)
        
        backend_name = type(secrets_manager.backend).__name__
        
        status = {
            "backend": backend_name,
            "operations": {
                "create": create_success,
                "read": read_success,
                "delete": delete_success,
                "list": list_success
            },
            "overall_health": all([create_success, read_success, delete_success, list_success])
        }
        
        return status
    except Exception as e:
        logger.error(f"Secrets health check failed: {e}")
        return {
            "backend": "unknown",
            "operations": {
                "create": False,
                "read": False,
                "delete": False,
                "list": False
            },
            "overall_health": False,
            "error": str(e)
        }