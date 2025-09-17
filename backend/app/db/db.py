"""
Unified database module containing models, database connection, and basic CRUD operations.
All database-related functionality consolidated in one file for simplicity.
"""
import uuid
import enum
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

# Database setup
engine = create_engine(settings.database_url)
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

# ========================================
# DATABASE MODELS
# ========================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="user")

class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
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

class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
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
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    business_id = Column(UUID(as_uuid=True), ForeignKey("businesses.id"), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    total_amount = Column(Float, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    business = relationship("Business", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

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