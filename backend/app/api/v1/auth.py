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
    """Get current authenticated user from JWT token with robust error handling."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify and decode JWT token
        token_data = verify_token(token)
        if token_data is None or not token_data.username:
            raise credentials_exception
        
        # Get user from database
        user = get_user_by_username(db, username=token_data.username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log unexpected errors and return 401 (never 500)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in get_current_user: {str(e)}")
        raise credentials_exception

def require_role(allowed_roles: List[str]):
    """Dependency factory for role-based access control with robust validation."""
    def role_checker(current_user: UserSchema = Depends(get_current_user)):
        try:
            # Extract user role - handle both string and enum values
            user_role = current_user.role
            if hasattr(user_role, 'value'):
                user_role = user_role.value
            
            # Normalize role strings for comparison
            user_role_str = str(user_role).lower()
            allowed_roles_str = [str(role).lower() for role in allowed_roles]
            
            # Check if user has required role or is admin
            if user_role_str not in allowed_roles_str and user_role_str != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {allowed_roles}, user role: {user_role}"
                )
            
            return current_user
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log unexpected errors and deny access
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in role validation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied due to role validation error"
            )
    
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
    
    return create_user(db=db, user=user)

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
    """Get current user information with complete profile data.
    
    Returns:
        UserSchema: Complete user profile including user_id, role, email, etc.
        
    Raises:
        401: Invalid, expired token or inactive user
        500: Never returned - all errors are handled gracefully
    """
    try:
        # Ensure all required fields are present
        if not hasattr(current_user, 'id') or not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user data",
            )
        
        if not hasattr(current_user, 'email') or not current_user.email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user email",
            )
            
        if not hasattr(current_user, 'role') or not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user role",
            )
        
        return current_user
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log unexpected errors and return 401 (never 500)
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in /me endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not retrieve user information",
        )