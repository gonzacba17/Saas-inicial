"""
Product management endpoints with role-based access control.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.db import (
    get_db, Product, ProductCRUD, Business, UserBusinessCRUD, UserBusinessRole
)
from app.schemas import (
    Product as ProductSchema, ProductCreate, ProductUpdate,
    User as UserSchema
)
from app.api.v1.auth import get_current_user

router = APIRouter()

def check_product_permission(
    product_id: UUID,
    current_user: UserSchema,
    db: Session,
    required_roles: Optional[List[UserBusinessRole]] = None
) -> bool:
    """Check if user has permission to access/modify product."""
    product = ProductCRUD.get_by_id(db, product_id)
    if not product:
        return False
    
    if required_roles is None:
        required_roles = [UserBusinessRole.owner, UserBusinessRole.manager]
    
    return UserBusinessCRUD.has_permission(db, current_user.id, product.business_id, required_roles)

def require_product_permission(
    product_id: UUID,
    current_user: UserSchema,
    db: Session,
    required_roles: Optional[List[UserBusinessRole]] = None
):
    """Raise HTTPException if user doesn't have permission to access product."""
    if not check_product_permission(product_id, current_user, db, required_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this product"
        )

def check_business_permission(
    business_id: UUID,
    current_user: UserSchema,
    db: Session,
    required_roles: Optional[List[UserBusinessRole]] = None
) -> bool:
    """Check if user has permission to access/modify business."""
    if required_roles is None:
        required_roles = [UserBusinessRole.owner, UserBusinessRole.manager]
    
    return UserBusinessCRUD.has_permission(db, current_user.id, business_id, required_roles)

def require_business_permission(
    business_id: UUID,
    current_user: UserSchema,
    db: Session,
    required_roles: Optional[List[UserBusinessRole]] = None
):
    """Raise HTTPException if user doesn't have permission to access business."""
    if not check_business_permission(business_id, current_user, db, required_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this business"
        )

# ========================================
# PRODUCT ENDPOINTS
# ========================================

@router.get("/", response_model=List[ProductSchema])
def list_products(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """List all available products."""
    products = ProductCRUD.get_all(db, skip=skip, limit=limit)
    return products

@router.get("/business/{business_id}", response_model=List[ProductSchema])
def list_business_products(
    business_id: UUID,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """List products for a specific business."""
    # Check if business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    products = ProductCRUD.get_by_business(db, business_id, skip=skip, limit=limit)
    return products

@router.post("/", response_model=ProductSchema)
def create_product(
    product: ProductCreate, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Create new product (business owners/managers only)."""
    # Check if business exists
    business = db.query(Business).filter(Business.id == product.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(product.business_id, current_user, db)
    
    return ProductCRUD.create(db, product.dict())

@router.get("/{product_id}", response_model=ProductSchema)
def get_product(
    product_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get product by ID."""
    product = ProductCRUD.get_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductSchema)
def update_product(
    product_id: UUID, 
    product_update: ProductUpdate, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Update product (business owners/managers only)."""
    product = ProductCRUD.get_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check permissions
    require_product_permission(product_id, current_user, db)
    
    update_data = product_update.dict(exclude_unset=True)
    return ProductCRUD.update(db, product_id, update_data)

@router.delete("/{product_id}")
def delete_product(
    product_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Delete product (soft delete, business owners/managers only)."""
    product = ProductCRUD.get_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check permissions
    require_product_permission(product_id, current_user, db)
    
    ProductCRUD.delete(db, product_id)
    return {"message": "Product deleted successfully"}
