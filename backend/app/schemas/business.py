from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class BusinessBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    business_type: Optional[str] = "general"

class BusinessCreate(BusinessBase):
    pass

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    business_type: Optional[str] = None
    is_active: Optional[bool] = None

class BusinessInDBBase(BusinessBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Business(BusinessInDBBase):
    pass

class BusinessInDB(BusinessInDBBase):
    pass