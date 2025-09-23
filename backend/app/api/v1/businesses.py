"""
Business management endpoints with role-based access control.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.db import (
    get_db, Business, UserBusiness, UserBusinessCRUD, UserBusinessRole
)
from app.schemas import (
    Business as BusinessSchema, BusinessCreate, BusinessUpdate,
    UserBusiness as UserBusinessSchema, UserBusinessCreate, UserBusinessUpdate,
    User as UserSchema
)
from app.api.v1.auth import get_current_user, require_role

router = APIRouter()

def check_business_permission(
    business_id: UUID,
    current_user: UserSchema,
    db: Session,
    required_roles: Optional[List[UserBusinessRole]] = None
) -> bool:
    """Check if user has permission to access/modify business."""
    if required_roles is None:
        required_roles = [UserBusinessRole.OWNER, UserBusinessRole.MANAGER]
    
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
# BUSINESS ENDPOINTS
# ========================================

@router.get("/", response_model=List[BusinessSchema])
def list_businesses(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """List all active businesses."""
    businesses = db.query(Business).filter(Business.is_active == True).offset(skip).limit(limit).all()
    return businesses

@router.post("/", response_model=BusinessSchema)
def create_business(
    business: BusinessCreate, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Create new business and associate current user as owner."""
    try:
        # Validate business data
        if not business.name or len(business.name.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business name is required and cannot be empty"
            )
        
        # Create business
        db_business = Business(**business.dict())
        db.add(db_business)
        db.commit()
        db.refresh(db_business)
        
        # Create user-business association as owner
        user_business_data = {
            "user_id": current_user.id,
            "business_id": db_business.id,
            "role": UserBusinessRole.OWNER
        }
        UserBusinessCRUD.create(db, user_business_data)
        
        return db_business
        
    except HTTPException:
        # Re-raise HTTP exceptions
        db.rollback()
        raise
    except Exception as e:
        # Handle unexpected errors
        db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating business: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating business"
        )

@router.get("/{business_id}", response_model=BusinessSchema)
def get_business(
    business_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get business by ID."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.put("/{business_id}", response_model=BusinessSchema)
def update_business(
    business_id: UUID, 
    business_update: BusinessUpdate, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Update business (owners and managers only)."""
    try:
        # Validate UUID format
        if not business_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid business ID format"
            )
        
        business = db.query(Business).filter(Business.id == business_id).first()
        if business is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Business not found"
            )
        
        # Check permissions
        require_business_permission(business_id, current_user, db)
        
        # Validate update data
        update_data = business_update.dict(exclude_unset=True)
        if "name" in update_data and (not update_data["name"] or len(update_data["name"].strip()) == 0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business name cannot be empty"
            )
        
        for field, value in update_data.items():
            setattr(business, field, value)
        
        db.commit()
        db.refresh(business)
        return business
        
    except HTTPException:
        # Re-raise HTTP exceptions
        db.rollback()
        raise
    except Exception as e:
        # Handle unexpected errors
        db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error updating business {business_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating business"
        )

@router.delete("/{business_id}")
def delete_business(
    business_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Delete business (soft delete, owners only)."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions (only owners can delete)
    require_business_permission(business_id, current_user, db, [UserBusinessRole.OWNER])
    
    business.is_active = False
    db.commit()
    return {"message": "Business deleted successfully"}

# ========================================
# USER-BUSINESS RELATIONSHIP ENDPOINTS
# ========================================

@router.get("/user-businesses", response_model=List[UserBusinessSchema])
def list_user_businesses(
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get all businesses for current user."""
    user_businesses = UserBusinessCRUD.get_user_businesses(db, current_user.id)
    return user_businesses

@router.post("/user-businesses", response_model=UserBusinessSchema)
def create_user_business(
    user_business: UserBusinessCreate, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Associate current user with a business."""
    # Check if business exists
    business = db.query(Business).filter(Business.id == user_business.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check if association already exists
    existing = UserBusinessCRUD.get_by_user_and_business(db, current_user.id, user_business.business_id)
    if existing:
        raise HTTPException(status_code=400, detail="User already associated with this business")
    
    user_business_data = user_business.dict()
    user_business_data["user_id"] = current_user.id
    
    return UserBusinessCRUD.create(db, user_business_data)

@router.delete("/user-businesses/{business_id}")
def remove_user_business(
    business_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Remove current user association with a business."""
    user_business = UserBusinessCRUD.get_by_user_and_business(db, current_user.id, business_id)
    if not user_business:
        raise HTTPException(status_code=404, detail="User business association not found")
    
    UserBusinessCRUD.delete(db, current_user.id, business_id)
    return {"message": "User business association removed successfully"}