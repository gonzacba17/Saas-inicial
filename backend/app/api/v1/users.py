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
from app.db.db import get_db, User, Business, Product, UserBusiness, UserBusinessCRUD, UserBusinessRole, Order, OrderItem, OrderCRUD, OrderItemCRUD, OrderStatus, AnalyticsCRUD, AIConversation, AIConversationCRUD, AIAssistantType
from app.schemas import Token, UserCreate, User as UserSchema, UserUpdate, Business as BusinessSchema, BusinessCreate, BusinessUpdate, Product as ProductSchema, ProductCreate, ProductUpdate, UserBusiness as UserBusinessSchema, UserBusinessCreate, UserBusinessUpdate, Order as OrderSchema, OrderCreate, OrderUpdate, OrderItem as OrderItemSchema, BusinessAnalytics, DateRangeStats, AIQueryRequest, AIResponse, AIConversation as AIConversationSchema, AIUsageStats
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
# USER-BUSINESS RELATIONSHIP ENDPOINTS
# ========================================

@router.get("/user-businesses", response_model=List[UserBusinessSchema])
def read_user_businesses(db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get all businesses for current user."""
    user_businesses = UserBusinessCRUD.get_user_businesses(db, current_user.id)
    return user_businesses

@router.post("/user-businesses", response_model=UserBusinessSchema)
def create_user_business(user_business: UserBusinessCreate, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
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
def delete_user_business(business_id: UUID, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Remove current user association with a business."""
    user_business = UserBusinessCRUD.get_by_user_and_business(db, current_user.id, business_id)
    if not user_business:
        raise HTTPException(status_code=404, detail="User business association not found")
    
    UserBusinessCRUD.delete(db, current_user.id, business_id)
    return {"message": "User business association removed successfully"}

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
    """Create new business and associate current user as owner."""
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

@router.get("/businesses/{business_id}", response_model=BusinessSchema)
def read_business(business_id: UUID, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get business by ID."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.put("/businesses/{business_id}", response_model=BusinessSchema)
def update_business(business_id: UUID, business_update: BusinessUpdate, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Update a business (only owners and managers)."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(business_id, current_user, db)
    
    update_data = business_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(business, field, value)
    
    db.commit()
    db.refresh(business)
    return business

@router.delete("/businesses/{business_id}")
def delete_business(business_id: UUID, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Delete a business (soft delete, only owners)."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions (only owners can delete)
    require_business_permission(business_id, current_user, db, [UserBusinessRole.OWNER])
    
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
    """Create new product (only business owners and managers)."""
    # Verify business exists
    business = db.query(Business).filter(Business.id == product.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(product.business_id, current_user, db)
    
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
    """Update a product (only business owners and managers)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check permissions
    require_business_permission(product.business_id, current_user, db)
    
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/products/{product_id}")
def delete_product(product_id: UUID, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Delete a product (soft delete, only business owners and managers)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check permissions
    require_business_permission(product.business_id, current_user, db)
    
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

# ========================================
# ORDER ENDPOINTS
# ========================================

@router.get("/orders", response_model=List[OrderSchema])
def read_user_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get all orders for current user."""
    orders = OrderCRUD.get_user_orders(db, current_user.id, skip=skip, limit=limit)
    return orders

@router.post("/orders", response_model=OrderSchema)
def create_order(order: OrderCreate, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Create a new order (checkout)."""
    # Verify business exists
    business = db.query(Business).filter(Business.id == order.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Calculate total amount and validate products
    total_amount = 0
    validated_items = []
    
    for item in order.items:
        # Get product and validate availability
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if not product.is_available:
            raise HTTPException(status_code=400, detail=f"Product {product.name} is not available")
        if product.business_id != order.business_id:
            raise HTTPException(status_code=400, detail=f"Product {product.name} does not belong to this business")
        
        # Use current product price
        unit_price = product.price
        total_price = item.quantity * unit_price
        total_amount += total_price
        
        validated_items.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": unit_price,
            "total_price": total_price
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
    for item in validated_items:
        item["order_id"] = db_order.id
        OrderItemCRUD.create(db, item)
    
    # Refresh order to include items
    db.refresh(db_order)
    return db_order

@router.get("/orders/{order_id}", response_model=OrderSchema)
def read_order(order_id: UUID, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get order by ID (only for order owner or business owner)."""
    order = OrderCRUD.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user is order owner or business owner
    is_order_owner = order.user_id == current_user.id
    is_business_owner = check_business_permission(order.business_id, current_user, db)
    
    if not (is_order_owner or is_business_owner):
        raise HTTPException(status_code=403, detail="Not enough permissions to view this order")
    
    return order

@router.put("/orders/{order_id}/status", response_model=OrderSchema)
def update_order_status(order_id: UUID, status_update: OrderUpdate, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Update order status (only business owners can update)."""
    order = OrderCRUD.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Only business owners can update order status
    require_business_permission(order.business_id, current_user, db)
    
    if status_update.status:
        # Validate status transition
        valid_statuses = [status.value for status in OrderStatus]
        if status_update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid order status")
        
        updated_order = OrderCRUD.update_status(db, order_id, OrderStatus(status_update.status))
        return updated_order
    
    return order

@router.get("/businesses/{business_id}/orders", response_model=List[OrderSchema])
def read_business_orders(business_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get all orders for a business (only business owners)."""
    # Verify business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(business_id, current_user, db)
    
    orders = OrderCRUD.get_business_orders(db, business_id, skip=skip, limit=limit)
    return orders

# ========================================
# ANALYTICS ENDPOINTS
# ========================================

@router.get("/businesses/{business_id}/analytics", response_model=BusinessAnalytics)
def get_business_analytics(business_id: UUID, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get analytics for a business (only business owners)."""
    # Verify business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(business_id, current_user, db)
    
    analytics_data = AnalyticsCRUD.get_business_analytics(db, business_id)
    analytics_data["business_name"] = business.name
    
    return analytics_data

@router.get("/businesses/{business_id}/analytics/daily")
def get_daily_sales(business_id: UUID, days: int = 30, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get daily sales data for a business (only business owners)."""
    # Verify business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(business_id, current_user, db)
    
    # Validate days parameter
    if days <= 0 or days > 365:
        raise HTTPException(status_code=400, detail="Days parameter must be between 1 and 365")
    
    daily_data = AnalyticsCRUD.get_daily_sales(db, business_id, days)
    return daily_data

@router.get("/businesses/{business_id}/analytics/date-range", response_model=DateRangeStats)
def get_date_range_analytics(
    business_id: UUID, 
    start_date: str, 
    end_date: str,
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get analytics for a specific date range (only business owners)."""
    from datetime import datetime
    
    # Verify business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Check permissions
    require_business_permission(business_id, current_user, db)
    
    # Parse dates
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DD)")
    
    if start_dt > end_dt:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    stats = AnalyticsCRUD.get_date_range_stats(db, business_id, start_dt, end_dt)
    return stats

# ========================================
# AI ASSISTANT ENDPOINTS
# ========================================

@router.post("/ai/chat", response_model=AIResponse)
async def chat_with_ai(query: AIQueryRequest, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Chat with AI assistant for business insights."""
    from app.services.ai_service import ai_service
    
    # If business_id is provided, verify permissions
    if query.business_id:
        business = db.query(Business).filter(Business.id == query.business_id).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        # Check if user has permission to access this business
        require_business_permission(query.business_id, current_user, db)
    
    # Process AI query
    result = await ai_service.process_query(db, current_user.id, query)
    return result

@router.get("/ai/conversations", response_model=List[AIConversationSchema])
def get_user_conversations(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get user's AI conversation history."""
    conversations = AIConversationCRUD.get_user_conversations(db, current_user.id, skip=skip, limit=limit)
    return conversations

@router.get("/ai/conversations/{conversation_id}", response_model=AIConversationSchema)
def get_conversation(conversation_id: UUID, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get specific AI conversation."""
    conversation = AIConversationCRUD.get_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check if user owns this conversation
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to view this conversation")
    
    return conversation

@router.get("/ai/conversations/by-type/{assistant_type}", response_model=List[AIConversationSchema])
def get_conversations_by_type(
    assistant_type: AIAssistantType, 
    skip: int = 0, 
    limit: int = 50, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get conversations by assistant type."""
    conversations = AIConversationCRUD.get_by_type(db, current_user.id, assistant_type, skip=skip, limit=limit)
    return conversations

@router.get("/ai/usage", response_model=AIUsageStats)
def get_ai_usage_stats(business_id: Optional[UUID] = None, db: Session = Depends(get_db), current_user: UserSchema = Depends(get_current_user)):
    """Get AI usage statistics for user or specific business."""
    if business_id:
        # Verify business permissions
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        require_business_permission(business_id, current_user, db)
    
    stats = AIConversationCRUD.get_usage_stats(db, current_user.id, business_id)
    return stats

@router.get("/businesses/{business_id}/ai/conversations", response_model=List[AIConversationSchema])
def get_business_conversations(
    business_id: UUID, 
    skip: int = 0, 
    limit: int = 50, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get AI conversations for a specific business."""
    # Verify business exists and user has permissions
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    require_business_permission(business_id, current_user, db)
    
    conversations = AIConversationCRUD.get_business_conversations(db, business_id, skip=skip, limit=limit)
    return conversations