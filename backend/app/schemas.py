"""
Unified Pydantic schemas for all models.
All data validation and serialization schemas consolidated in one file for simplicity.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

# ========================================
# TOKEN SCHEMAS
# ========================================

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ========================================
# USER SCHEMAS
# ========================================

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDBBase(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

# ========================================
# BUSINESS SCHEMAS
# ========================================

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

# ========================================
# PRODUCT SCHEMAS
# ========================================

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    business_id: UUID

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None

class ProductInDBBase(ProductBase):
    id: UUID
    business_id: UUID
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Product(ProductInDBBase):
    pass

class ProductInDB(ProductInDBBase):
    pass

# ========================================
# ORDER SCHEMAS (for future use)
# ========================================

class OrderItemBase(BaseModel):
    product_id: UUID
    quantity: int
    unit_price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: UUID
    order_id: UUID
    total_price: float

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    business_id: UUID
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    items: list[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class OrderInDBBase(OrderBase):
    id: UUID
    user_id: UUID
    status: str
    total_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Order(OrderInDBBase):
    items: list[OrderItem] = []

class OrderInDB(OrderInDBBase):
    pass