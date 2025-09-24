"""
Unified database module containing models, database connection, and basic CRUD operations.
All database-related functionality consolidated in one file for simplicity.
"""
import uuid
import enum
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey, Enum, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

# Custom UUID type that works with both PostgreSQL and SQLite
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type when available, otherwise uses CHAR(36) for SQLite.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PGUUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value

# Database setup
engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ========================================
# ENUMS
# ========================================

class OrderStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class UserBusinessRole(enum.Enum):
    owner = "owner"
    manager = "manager"
    employee = "employee"

class AIAssistantType(enum.Enum):
    PRODUCT_SUGGESTION = "product_suggestion"
    SALES_ANALYSIS = "sales_analysis"
    BUSINESS_INSIGHTS = "business_insights"
    GENERAL_QUERY = "general_query"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    AUTHORIZED = "authorized"
    IN_PROCESS = "in_process"
    IN_MEDIATION = "in_mediation"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    CHARGED_BACK = "charged_back"

# ========================================
# DATABASE MODELS
# ========================================

class UserRole(enum.Enum):
    """User roles for system-wide permissions."""
    user = "user"
    owner = "owner"  
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    business_associations = relationship("UserBusiness", back_populates="user")

class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    address = Column(String)
    phone = Column(String)
    email = Column(String)
    business_type = Column(String, default="general")  # restaurant, store, service, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="business")
    orders = relationship("Order", back_populates="business")
    user_associations = relationship("UserBusiness", back_populates="business")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    business_id = Column(GUID(), ForeignKey("businesses.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String)
    image_url = Column(String)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    business = relationship("Business", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    business_id = Column(GUID(), ForeignKey("businesses.id"), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = Column(Float, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    business = relationship("Business", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    order_id = Column(GUID(), ForeignKey("orders.id"), nullable=False)
    product_id = Column(GUID(), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class UserBusiness(Base):
    __tablename__ = "user_businesses"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    business_id = Column(GUID(), ForeignKey("businesses.id"), nullable=False)
    role = Column(Enum(UserBusinessRole), default=UserBusinessRole.owner)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="business_associations")
    business = relationship("Business", back_populates="user_associations")

class AIConversation(Base):
    __tablename__ = "ai_conversations"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    business_id = Column(GUID(), ForeignKey("businesses.id"), nullable=True)
    assistant_type = Column(Enum(AIAssistantType), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0)
    response_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    business = relationship("Business")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    order_id = Column(GUID(), ForeignKey("orders.id"), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    business_id = Column(GUID(), ForeignKey("businesses.id"), nullable=False)
    
    # MercadoPago specific fields
    mercadopago_payment_id = Column(String, unique=True, index=True)
    preference_id = Column(String, index=True)
    external_reference = Column(String, index=True)
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String, default="ARS")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String)
    payment_type = Column(String)
    
    # Transaction details
    transaction_amount = Column(Float)
    net_received_amount = Column(Float)
    total_paid_amount = Column(Float)
    
    # Metadata
    payment_metadata = Column(Text)  # JSON string for additional data
    webhook_data = Column(Text)  # Store webhook payload
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    order = relationship("Order", back_populates="payments")
    user = relationship("User")
    business = relationship("Business")

# ========================================
# DATABASE CONNECTION
# ========================================

def get_db():
    """Database dependency for FastAPI endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)

# ========================================
# BASIC CRUD OPERATIONS
# ========================================

class UserCRUD:
    """Basic CRUD operations for User model."""
    
    @staticmethod
    def create(db, user_data):
        """Create a new user."""
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_by_id(db, user_id):
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_by_email(db, email):
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_username(db, username):
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_all(db, skip=0, limit=100):
        """Get all users with pagination."""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db, user_id, update_data):
        """Update user by ID."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            for field, value in update_data.items():
                setattr(db_user, field, value)
            db.commit()
            db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete(db, user_id):
        """Soft delete user by ID."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db_user.is_active = False
            db.commit()
        return db_user

class BusinessCRUD:
    """Basic CRUD operations for Business model."""
    
    @staticmethod
    def create(db, business_data):
        """Create a new business."""
        db_business = Business(**business_data)
        db.add(db_business)
        db.commit()
        db.refresh(db_business)
        return db_business
    
    @staticmethod
    def get_by_id(db, business_id):
        """Get business by ID."""
        return db.query(Business).filter(Business.id == business_id).first()
    
    @staticmethod
    def get_all(db, skip=0, limit=100):
        """Get all active businesses with pagination."""
        return db.query(Business).filter(Business.is_active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all_active(db):
        """Get all active businesses without pagination."""
        return db.query(Business).filter(Business.is_active == True).all()
    
    @staticmethod
    def update(db, business_id, update_data):
        """Update business by ID."""
        db_business = db.query(Business).filter(Business.id == business_id).first()
        if db_business:
            for field, value in update_data.items():
                setattr(db_business, field, value)
            db.commit()
            db.refresh(db_business)
        return db_business
    
    @staticmethod
    def delete(db, business_id):
        """Soft delete business by ID."""
        db_business = db.query(Business).filter(Business.id == business_id).first()
        if db_business:
            db_business.is_active = False
            db.commit()
        return db_business

class ProductCRUD:
    """Basic CRUD operations for Product model."""
    
    @staticmethod
    def create(db, product_data):
        """Create a new product."""
        db_product = Product(**product_data)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    
    @staticmethod
    def get_by_id(db, product_id):
        """Get product by ID."""
        return db.query(Product).filter(Product.id == product_id).first()
    
    @staticmethod
    def get_all(db, skip=0, limit=100):
        """Get all available products with pagination."""
        return db.query(Product).filter(Product.is_available == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_business(db, business_id, skip=0, limit=100):
        """Get products by business ID."""
        return db.query(Product).filter(
            Product.business_id == business_id,
            Product.is_available == True
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db, product_id, update_data):
        """Update product by ID."""
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if db_product:
            for field, value in update_data.items():
                setattr(db_product, field, value)
            db.commit()
            db.refresh(db_product)
        return db_product
    
    @staticmethod
    def delete(db, product_id):
        """Soft delete product by ID."""
        db_product = db.query(Product).filter(Product.id == product_id).first()
        if db_product:
            db_product.is_available = False
            db.commit()
        return db_product

class UserBusinessCRUD:
    """Basic CRUD operations for UserBusiness model."""
    
    @staticmethod
    def create(db, user_business_data):
        """Create a new user-business association."""
        db_user_business = UserBusiness(**user_business_data)
        db.add(db_user_business)
        db.commit()
        db.refresh(db_user_business)
        return db_user_business
    
    @staticmethod
    def get_by_user_and_business(db, user_id, business_id):
        """Get user-business association by user and business ID."""
        return db.query(UserBusiness).filter(
            UserBusiness.user_id == user_id,
            UserBusiness.business_id == business_id,
            UserBusiness.is_active == True
        ).first()
    
    @staticmethod
    def get_user_businesses(db, user_id):
        """Get all businesses for a user."""
        return db.query(UserBusiness).filter(
            UserBusiness.user_id == user_id,
            UserBusiness.is_active == True
        ).all()
    
    @staticmethod
    def get_business_users(db, business_id):
        """Get all users for a business."""
        return db.query(UserBusiness).filter(
            UserBusiness.business_id == business_id,
            UserBusiness.is_active == True
        ).all()
    
    @staticmethod
    def is_user_owner(db, user_id, business_id):
        """Check if user is owner of business."""
        association = db.query(UserBusiness).filter(
            UserBusiness.user_id == user_id,
            UserBusiness.business_id == business_id,
            UserBusiness.role == UserBusinessRole.owner,
            UserBusiness.is_active == True
        ).first()
        return association is not None
    
    @staticmethod
    def has_permission(db, user_id, business_id, required_roles=None):
        """Check if user has permission to access business."""
        if required_roles is None:
            required_roles = [UserBusinessRole.owner, UserBusinessRole.manager]
        
        association = db.query(UserBusiness).filter(
            UserBusiness.user_id == user_id,
            UserBusiness.business_id == business_id,
            UserBusiness.role.in_(required_roles),
            UserBusiness.is_active == True
        ).first()
        return association is not None
    
    @staticmethod
    def delete(db, user_id, business_id):
        """Remove user-business association."""
        db_user_business = db.query(UserBusiness).filter(
            UserBusiness.user_id == user_id,
            UserBusiness.business_id == business_id
        ).first()
        if db_user_business:
            db_user_business.is_active = False
            db.commit()
        return db_user_business

class OrderCRUD:
    """Basic CRUD operations for Order model."""
    
    @staticmethod
    def create(db, order_data):
        """Create a new order."""
        db_order = Order(**order_data)
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    
    @staticmethod
    def get_by_id(db, order_id):
        """Get order by ID."""
        return db.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def get_user_orders(db, user_id, skip=0, limit=100):
        """Get all orders for a user."""
        return db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_business_orders(db, business_id, skip=0, limit=100):
        """Get all orders for a business."""
        return db.query(Order).filter(Order.business_id == business_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_status(db, order_id, new_status):
        """Update order status."""
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if db_order:
            db_order.status = new_status
            db.commit()
            db.refresh(db_order)
        return db_order
    
    @staticmethod
    def calculate_total(db, order_items):
        """Calculate total amount for order items."""
        total = 0
        for item in order_items:
            total += item.get("quantity", 1) * item.get("unit_price", 0)
        return total

class OrderItemCRUD:
    """Basic CRUD operations for OrderItem model."""
    
    @staticmethod
    def create(db, order_item_data):
        """Create a new order item."""
        db_order_item = OrderItem(**order_item_data)
        db.add(db_order_item)
        db.commit()
        db.refresh(db_order_item)
        return db_order_item
    
    @staticmethod
    def get_by_order(db, order_id):
        """Get all items for an order."""
        return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    
    @staticmethod
    def create_bulk(db, order_items_data):
        """Create multiple order items at once."""
        order_items = []
        for item_data in order_items_data:
            db_order_item = OrderItem(**item_data)
            db.add(db_order_item)
            order_items.append(db_order_item)
        db.commit()
        for item in order_items:
            db.refresh(item)
        return order_items

class AnalyticsCRUD:
    """Analytics and statistics operations."""
    
    @staticmethod
    def get_business_analytics(db, business_id):
        """Get analytics for a specific business."""
        from sqlalchemy import func, and_
        
        # Basic business stats
        total_orders = db.query(func.count(Order.id)).filter(Order.business_id == business_id).scalar()
        total_revenue = db.query(func.sum(Order.total_amount)).filter(Order.business_id == business_id).scalar() or 0
        
        # Orders by status
        pending_orders = db.query(func.count(Order.id)).filter(
            and_(Order.business_id == business_id, Order.status == OrderStatus.PENDING)
        ).scalar()
        
        completed_orders = db.query(func.count(Order.id)).filter(
            and_(Order.business_id == business_id, Order.status == OrderStatus.DELIVERED)
        ).scalar()
        
        # Top products by quantity sold
        top_products = db.query(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.total_price).label('total_revenue')
        ).join(OrderItem, Product.id == OrderItem.product_id)\
         .join(Order, OrderItem.order_id == Order.id)\
         .filter(Order.business_id == business_id)\
         .group_by(Product.id, Product.name)\
         .order_by(func.sum(OrderItem.quantity).desc())\
         .limit(5).all()
        
        return {
            "business_id": business_id,
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "top_products": [
                {
                    "product_id": product.id,
                    "product_name": product.name,
                    "total_quantity": int(product.total_quantity),
                    "total_revenue": float(product.total_revenue)
                }
                for product in top_products
            ]
        }
    
    @staticmethod
    def get_date_range_stats(db, business_id, start_date, end_date):
        """Get statistics for a date range."""
        from sqlalchemy import func, and_
        
        orders_in_range = db.query(Order).filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).all()
        
        total_orders = len(orders_in_range)
        total_revenue = sum(order.total_amount for order in orders_in_range)
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "average_order_value": float(average_order_value)
        }
    
    @staticmethod
    def get_daily_sales(db, business_id, days=30):
        """Get daily sales for the last N days."""
        from sqlalchemy import func, and_
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        daily_stats = db.query(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('orders'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            and_(
                Order.business_id == business_id,
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).group_by(func.date(Order.created_at))\
         .order_by(func.date(Order.created_at)).all()
        
        return [
            {
                "date": stat.date.isoformat(),
                "orders": stat.orders,
                "revenue": float(stat.revenue or 0)
            }
            for stat in daily_stats
        ]

class AIConversationCRUD:
    """CRUD operations for AI conversations."""
    
    @staticmethod
    def create(db, conversation_data):
        """Create a new AI conversation record."""
        db_conversation = AIConversation(**conversation_data)
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        return db_conversation
    
    @staticmethod
    def get_by_id(db, conversation_id):
        """Get conversation by ID."""
        return db.query(AIConversation).filter(AIConversation.id == conversation_id).first()
    
    @staticmethod
    def get_user_conversations(db, user_id, skip=0, limit=100):
        """Get all conversations for a user."""
        return db.query(AIConversation).filter(
            AIConversation.user_id == user_id
        ).order_by(AIConversation.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_business_conversations(db, business_id, skip=0, limit=100):
        """Get all conversations for a business."""
        return db.query(AIConversation).filter(
            AIConversation.business_id == business_id
        ).order_by(AIConversation.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_type(db, user_id, assistant_type, skip=0, limit=50):
        """Get conversations by assistant type."""
        return db.query(AIConversation).filter(
            AIConversation.user_id == user_id,
            AIConversation.assistant_type == assistant_type
        ).order_by(AIConversation.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_usage_stats(db, user_id, business_id=None):
        """Get usage statistics for a user or business."""
        from sqlalchemy import func
        
        query = db.query(
            func.count(AIConversation.id).label('total_conversations'),
            func.sum(AIConversation.tokens_used).label('total_tokens'),
            func.avg(AIConversation.response_time_ms).label('avg_response_time')
        ).filter(AIConversation.user_id == user_id)
        
        if business_id:
            query = query.filter(AIConversation.business_id == business_id)
        
        result = query.first()
        return {
            "total_conversations": result.total_conversations or 0,
            "total_tokens": result.total_tokens or 0,
            "avg_response_time": float(result.avg_response_time or 0)
        }
    
    @staticmethod
    def delete_old_conversations(db, cutoff_date):
        """Delete conversations older than cutoff_date."""
        deleted_count = db.query(AIConversation).filter(
            AIConversation.created_at < cutoff_date
        ).delete()
        db.commit()
        return deleted_count

class PaymentCRUD:
    """CRUD operations for Payment model."""
    
    @staticmethod
    def create(db, payment_data):
        """Create a new payment record."""
        db_payment = Payment(**payment_data)
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        return db_payment
    
    @staticmethod
    def get_by_id(db, payment_id):
        """Get payment by ID."""
        return db.query(Payment).filter(Payment.id == payment_id).first()
    
    @staticmethod
    def get_by_order_id(db, order_id):
        """Get all payments for an order."""
        return db.query(Payment).filter(Payment.order_id == order_id).all()
    
    @staticmethod
    def get_by_mercadopago_id(db, mercadopago_payment_id):
        """Get payment by MercadoPago payment ID."""
        return db.query(Payment).filter(
            Payment.mercadopago_payment_id == mercadopago_payment_id
        ).first()
    
    @staticmethod
    def get_by_external_reference(db, external_reference):
        """Get payment by external reference (order ID)."""
        return db.query(Payment).filter(
            Payment.external_reference == external_reference
        ).first()
    
    @staticmethod
    def update_status(db, payment_id, status, payment_data=None):
        """Update payment status and optional additional data."""
        db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if db_payment:
            db_payment.status = status
            if payment_data:
                # Update additional fields from MercadoPago
                for field, value in payment_data.items():
                    if hasattr(db_payment, field):
                        setattr(db_payment, field, value)
            db.commit()
            db.refresh(db_payment)
        return db_payment
    
    @staticmethod
    def get_business_payments(db, business_id, skip=0, limit=100):
        """Get all payments for a business."""
        return db.query(Payment).filter(
            Payment.business_id == business_id
        ).order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_payments(db, user_id, skip=0, limit=100):
        """Get all payments for a user."""
        return db.query(Payment).filter(
            Payment.user_id == user_id
        ).order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_payments_by_status(db, status, skip=0, limit=100):
        """Get payments by status."""
        return db.query(Payment).filter(
            Payment.status == status
        ).order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()