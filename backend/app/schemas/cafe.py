from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class CafeBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class CafeCreate(CafeBase):
    pass

class CafeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class CafeInDBBase(CafeBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Cafe(CafeInDBBase):
    pass

class CafeInDB(CafeInDBBase):
    pass