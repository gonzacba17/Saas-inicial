"""
Unified services module for authentication and business logic.
All service functions consolidated in one file for simplicity.
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.db import User, UserCRUD
from app.schemas import UserCreate, TokenData

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ========================================
# PASSWORD UTILITIES
# ========================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

# ========================================
# JWT TOKEN UTILITIES
# ========================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
        return token_data
    except JWTError:
        return None

# ========================================
# USER SERVICES
# ========================================

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return UserCRUD.get_by_email(db, email)

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return UserCRUD.get_by_username(db, username)

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    # Check if user is active
    if not user.is_active:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user. Please contact support."
        )
    return user

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    from app.db.db import UserRole
    hashed_password = get_password_hash(user.password)
    user_data = {
        "email": user.email,
        "username": user.username,
        "hashed_password": hashed_password,
        "role": getattr(user, 'role', UserRole.user),  # Default to user role
        "is_active": True,
        "is_superuser": False
    }
    return UserCRUD.create(db, user_data)

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get list of users."""
    return UserCRUD.get_all(db, skip, limit)

def get_user(db: Session, user_id: str):
    """Get user by ID."""
    return UserCRUD.get_by_id(db, user_id)

def update_user(db: Session, user_id: str, user_update):
    """Update user."""
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    return UserCRUD.update(db, user_id, update_data)