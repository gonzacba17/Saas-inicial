from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.dependencies import get_db, get_current_user
from app.db.models import User, Business
from app.schemas.business import Business as BusinessSchema, BusinessCreate, BusinessUpdate

router = APIRouter()

@router.get("/", response_model=List[BusinessSchema])
def read_businesses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve businesses.
    """
    businesses = db.query(Business).filter(Business.is_active == True).offset(skip).limit(limit).all()
    return businesses

@router.post("/", response_model=BusinessSchema)
def create_business(
    business: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new business.
    """
    db_business = Business(**business.dict())
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    return db_business

@router.get("/{business_id}", response_model=BusinessSchema)
def read_business(
    business_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get business by ID.
    """
    business = db.query(Business).filter(Business.id == business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.put("/{business_id}", response_model=BusinessSchema)
def update_business(
    business_id: UUID,
    business_update: BusinessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a business.
    """
    business = db.query(Business).filter(Business.id == business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    update_data = business_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(business, field, value)
    
    db.commit()
    db.refresh(business)
    return business

@router.delete("/{business_id}")
def delete_business(
    business_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a business (soft delete).
    """
    business = db.query(Business).filter(Business.id == business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business.is_active = False
    db.commit()
    return {"message": "Business deleted successfully"}