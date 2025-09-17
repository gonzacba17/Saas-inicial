"""
Unified API endpoints for users, authentication, businesses, and products.
All main application endpoints consolidated in one file for simplicity.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

# Core imports
from app.core.config import settings
from app.db.db import get_db, User, Business, Product
from app.schemas import Token, UserCreate, User as UserSchema, UserUpdate, Business as BusinessSchema, BusinessCreate, BusinessUpdate, Product as ProductSchema, ProductCreate, ProductUpdate
from app.services import verify_token, get_user_by_username, get_user_by_email, authenticate_user, create_access_token, create_user, get_users, get_user, update_user

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

# ========================================
# AUTHENTICATION ENDPOINTS
# ========================================

@router.post("/auth/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account."""
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    return create_user(db=db, user=user)

@router.post("/auth/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 compatible token login, get an access token for future requests."""
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
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/refresh", response_model=Token)
def refresh_token(current_user: UserSchema = Depends(get_current_user)):
    """Refresh access token for authenticated user."""
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/auth/me", response_model=UserSchema)
def read_users_me(current_user: UserSchema = Depends(get_current_user)):
    """Get current user information."""
    return current_user

# ========================================
# USER MANAGEMENT ENDPOINTS
# ========================================

@router.get("/users", response_model=List[UserSchema])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get list of users."""
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=UserSchema)
def read_user(user_id: UUID, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get user by ID."""
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/users/{user_id}", response_model=UserSchema)
def update_user_endpoint(user_id: UUID, user_update: UserUpdate, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Update user by ID."""
    db_user = update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# ========================================
# BUSINESS ENDPOINTS
# ========================================

@router.get("/businesses", response_model=List[BusinessSchema])
def read_businesses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Retrieve businesses."""
    businesses = db.query(Business).filter(Business.is_active == True).offset(skip).limit(limit).all()
    return businesses

@router.post("/businesses", response_model=BusinessSchema)
def create_business(business: BusinessCreate, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Create new business."""
    db_business = Business(**business.dict())
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    return db_business

@router.get("/businesses/{business_id}", response_model=BusinessSchema)
def read_business(business_id: UUID, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get business by ID."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.put("/businesses/{business_id}", response_model=BusinessSchema)
def update_business(business_id: UUID, business_update: BusinessUpdate, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Update a business."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    update_data = business_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(business, field, value)
    
    db.commit()
    db.refresh(business)
    return business

@router.delete("/businesses/{business_id}")
def delete_business(business_id: UUID, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Delete a business (soft delete)."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business.is_active = False
    db.commit()
    return {"message": "Business deleted successfully"}

# ========================================
# PRODUCT ENDPOINTS
# ========================================

@router.get("/products", response_model=List[ProductSchema])
def read_products(
    skip: int = 0,
    limit: int = 100,
    business_id: Optional[UUID] = Query(None, description="Filter by business ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """Retrieve products with optional filters."""
    query = db.query(Product)
    
    if business_id:
        query = query.filter(Product.business_id == business_id)
    if category:
        query = query.filter(Product.category == category)
    if is_available is not None:
        query = query.filter(Product.is_available == is_available)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.post("/products", response_model=ProductSchema)
def create_product(product: ProductCreate, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Create new product."""
    # Verify business exists
    business = db.query(Business).filter(Business.id == product.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/products/{product_id}", response_model=ProductSchema)
def read_product(product_id: UUID, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/products/{product_id}", response_model=ProductSchema)
def update_product(product_id: UUID, product_update: ProductUpdate, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Update a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/products/{product_id}")
def delete_product(product_id: UUID, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Delete a product (soft delete)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.is_available = False
    db.commit()
    return {"message": "Product deleted successfully"}

@router.get("/businesses/{business_id}/products", response_model=List[ProductSchema])
def read_business_products(business_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get all products for a specific business."""
    # Verify business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    products = db.query(Product).filter(
        Product.business_id == business_id,
        Product.is_available == True
    ).offset(skip).limit(limit).all()
    
    return products