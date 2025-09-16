from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.db.models import OrderStatus

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
    cafe_id: UUID
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None

class OrderInDBBase(OrderBase):
    id: UUID
    user_id: UUID
    status: OrderStatus
    total_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Order(OrderInDBBase):
    items: List[OrderItem] = []

class OrderInDB(OrderInDBBase):
    pass