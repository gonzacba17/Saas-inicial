"""
User management endpoints for CRUD operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.db import get_db
from app.schemas import User as UserSchema, UserUpdate
from app.services import get_users, get_user, update_user
from app.api.v1.auth import get_current_user, require_role

router = APIRouter()

# ========================================
# USER MANAGEMENT ENDPOINTS
# ========================================

@router.get("", response_model=List[UserSchema])
def list_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(require_role(["admin"]))
):
    """Get list of users (admin only)."""
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserSchema)
def get_user_by_id(
    user_id: UUID, 
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """Get user by ID (own profile or admin)."""
    # Users can only access their own profile unless they're admin
    user_role = current_user.role
    if hasattr(user_role, 'value'):
        user_role = user_role.value
    
    if current_user.id != user_id and str(user_role).lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this user"
        )
    
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserSchema)
def update_user_endpoint(
    user_id: UUID, 
    user_update: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """Update user by ID (own profile or admin)."""
    # Users can only update their own profile unless they're admin
    user_role = current_user.role
    if hasattr(user_role, 'value'):
        user_role = user_role.value
    
    if current_user.id != user_id and str(user_role).lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user"
        )
    
    db_user = update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Note: /me endpoint is handled in auth.py to avoid duplication