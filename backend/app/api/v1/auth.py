"""
Authentication endpoints for user registration, login, and JWT management.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.config import settings
from app.db.db import get_db, User, UserBusinessRole
from app.schemas import Token, UserCreate, User as UserSchema, UserUpdate
from app.services import (
    verify_token, get_user_by_username, get_user_by_email, authenticate_user,
    create_access_token, create_user, get_users, get_user, update_user
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_str}/auth/login")

# ========================================
# AUTHENTICATION DEPENDENCY
# ========================================

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(token)
    if token_data is None:
        raise credentials_exception
    
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def require_role(allowed_roles: List[str]):
    """Dependency factory for role-based access control."""
    def role_checker(current_user: UserSchema = Depends(get_current_user)):
        if current_user.role not in allowed_roles and "admin" not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker

# ========================================
# AUTHENTICATION ENDPOINTS
# ========================================

@router.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account."""
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Set default role if not provided
    user_data = user.dict()
    if 'role' not in user_data or not user_data['role']:
        user_data['role'] = 'user'
    
    return create_user(db=db, user=UserCreate(**user_data))

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": str(user.id),
        "role": user.role
    }

@router.post("/refresh", response_model=Token)
def refresh_token(current_user: UserSchema = Depends(get_current_user)):
    """Refresh JWT token for authenticated user."""
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": str(current_user.id),
        "role": current_user.role
    }

@router.get("/me", response_model=UserSchema)
def get_current_user_info(current_user: UserSchema = Depends(get_current_user)):
    """Get current user information."""
    return current_user