"""
Order management endpoints with role-based access control.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.db import (
    get_db, Order, OrderItem, OrderCRUD, OrderItemCRUD, OrderStatus,
    Business, Product, UserBusinessCRUD, UserBusinessRole
)
from app.schemas import (
    Order as OrderSchema, OrderCreate, OrderUpdate,
    OrderItem as OrderItemSchema, User as UserSchema
)
from app.api.v1.auth import get_current_user

router = APIRouter()

def check_order_permission(
    order_id: UUID,
    current_user: UserSchema,
    db: Session,
    required_roles: Optional[List[UserBusinessRole]] = None
) -> bool:
    """Check if user has permission to access/modify order."""
    order = OrderCRUD.get_by_id(db, order_id)
    if not order:
        return False
    
    # Order owners can always access their orders
    if order.user_id == current_user.id:
        return True
    
    # Business owners/managers can access orders for their business
    if required_roles is None:
        required_roles = [UserBusinessRole.owner, UserBusinessRole.manager]
    
    return UserBusinessCRUD.has_permission(db, current_user.id, order.business_id, required_roles)

def require_order_permission(
    order_id: UUID,
    current_user: UserSchema,
    db: Session,
    required_roles: Optional[List[UserBusinessRole]] = None
):
    """Raise HTTPException if user doesn't have permission to access order."""
    if not check_order_permission(order_id, current_user, db, required_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this order"
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
# ORDER ENDPOINTS
# ========================================

@router.get("/", response_model=List[OrderSchema])
def list_user_orders(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """List current user's orders."""
    orders = OrderCRUD.get_user_orders(db, current_user.id, skip=skip, limit=limit)
    return orders

@router.get("/business/{business_id}", response_model=List[OrderSchema])
def list_business_orders(
    business_id: UUID,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """List orders for a specific business (business owners/managers only)."""
    # Check if business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(business_id, current_user, db)
    
    orders = OrderCRUD.get_business_orders(db, business_id, skip=skip, limit=limit)
    return orders

@router.post("/", response_model=OrderSchema)
def create_order(
    order: OrderCreate, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Create new order."""
    # Check if business exists
    business = db.query(Business).filter(Business.id == order.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Validate products exist and belong to the business
    total_amount = 0
    order_items_data = []
    
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.business_id != order.business_id:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} does not belong to this business")
        if not product.is_available:
            raise HTTPException(status_code=400, detail=f"Product {product.name} is not available")
        
        item_total = item.quantity * product.price
        total_amount += item_total
        
        order_items_data.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": product.price,
            "total_price": item_total
        })
    
    # Create order
    order_data = {
        "user_id": current_user.id,
        "business_id": order.business_id,
        "status": OrderStatus.PENDING,
        "total_amount": total_amount,
        "notes": order.notes
    }
    
    db_order = OrderCRUD.create(db, order_data)
    
    # Create order items
    for item_data in order_items_data:
        item_data["order_id"] = db_order.id
    
    OrderItemCRUD.create_bulk(db, order_items_data)
    
    # Refresh to get items
    db.refresh(db_order)
    return db_order

@router.get("/{order_id}", response_model=OrderSchema)
def get_order(
    order_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get order by ID."""
    order = OrderCRUD.get_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions
    require_order_permission(order_id, current_user, db)
    
    return order

@router.put("/{order_id}/status", response_model=OrderSchema)
def update_order_status(
    order_id: UUID,
    new_status: OrderStatus,
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Update order status (business owners/managers only)."""
    order = OrderCRUD.get_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Only business owners/managers can update order status
    if not check_business_permission(order.business_id, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update order status"
        )
    
    return OrderCRUD.update_status(db, order_id, new_status)

@router.put("/{order_id}", response_model=OrderSchema)
def update_order(
    order_id: UUID, 
    order_update: OrderUpdate, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Update order (order owner or business owners/managers only)."""
    order = OrderCRUD.get_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions
    require_order_permission(order_id, current_user, db)
    
    # Only allow certain updates based on order status
    if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
        raise HTTPException(
            status_code=400, 
            detail="Cannot update completed or cancelled orders"
        )
    
    update_data = order_update.dict(exclude_unset=True)
    
    # Update order fields
    for field, value in update_data.items():
        if field != "items":  # Don't update items directly
            setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    return order

@router.get("/{order_id}/items", response_model=List[OrderItemSchema])
def get_order_items(
    order_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get order items."""
    order = OrderCRUD.get_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions
    require_order_permission(order_id, current_user, db)
    
    items = OrderItemCRUD.get_by_order(db, order_id)
    return items
