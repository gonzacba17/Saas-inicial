"""
Unified database module containing models, database connection, and basic CRUD operations.
All database-related functionality consolidated in one file for simplicity.
"""
import os
import uuid
import enum
import logging
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey, Enum, TypeDecorator, CHAR, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Configure logging for database module
logger = logging.getLogger(__name__)

# Global engine variable - NOT created automatically
_engine = None
Base = declarative_base()

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

# Database setup with proper UTF-8 encoding and logging
import logging
from app.core.security import get_database_url

def get_engine():
    """Get database engine, creating it only if needed."""
    global _engine
    if _engine is not None:
        return _engine
    
    # Check environment
    testing = os.getenv('TESTING', 'false').lower() == 'true'
    use_sqlite = os.getenv('USE_SQLITE', 'false').lower() == 'true'
    
    # Choose database type
    if testing or use_sqlite:
        # SQLite configuration
        if testing:
            db_url = "sqlite:///:memory:"
            logger.info("Using in-memory SQLite database for testing")
        else:
            sqlite_file = os.getenv('SQLITE_FILE', 'app/db/app.db')
            
            # Get absolute path from backend directory
            if not os.path.isabs(sqlite_file):
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                sqlite_file = os.path.join(backend_dir, sqlite_file)
            
            # Ensure directory exists
            db_dir = os.path.dirname(sqlite_file)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            # Convert to absolute path with forward slashes for SQLite URL
            sqlite_path = os.path.abspath(sqlite_file).replace("\\", "/")
            
            db_url = f"sqlite:///{sqlite_path}"
            logger.info(f"Using SQLite database: {sqlite_path}")
        
        # Create SQLite engine
        connect_args = {"check_same_thread": False}
        if testing:
            connect_args["timeout"] = 5
        else:
            connect_args["timeout"] = 30
            
        _engine = create_engine(db_url, connect_args=connect_args, echo=False)
        
        # Configure SQLite pragmas
        from sqlalchemy import event
        
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            if testing:
                cursor.execute("PRAGMA journal_mode=MEMORY")
                cursor.execute("PRAGMA synchronous=OFF")
                cursor.execute("PRAGMA temp_store=MEMORY")
            else:
                # Use DELETE mode instead of WAL for WSL compatibility
                try:
                    cursor.execute("PRAGMA journal_mode=WAL")
                except Exception:
                    # Fallback to DELETE mode for WSL/Windows filesystem issues
                    cursor.execute("PRAGMA journal_mode=DELETE")
                cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    else:
        # PostgreSQL configuration - use secure database URL
        db_url = get_database_url()
        logger.info("Using PostgreSQL database")
        
        _engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
            echo=False,
            connect_args={
                "client_encoding": "utf8",
                "options": "-c client_encoding=utf8"
            }
        )
    
    return _engine

def reset_engine():
    """Reset and dispose of the current engine."""
    global _engine
    if _engine is not None:
        try:
            _engine.dispose()
        except Exception:
            pass
        _engine = None

def get_session():
    """Get a new database session."""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def get_db():
    """Database dependency for FastAPI endpoints."""
    db = get_session()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """Create all database tables."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

# ========================================
# DATABASE CONNECTION
# ========================================

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

class ComprobanteType(enum.Enum):
    FACTURA_A = "factura_a"
    FACTURA_B = "factura_b"
    FACTURA_C = "factura_c"
    NOTA_CREDITO = "nota_credito"
    NOTA_DEBITO = "nota_debito"
    RECIBO = "recibo"
    PRESUPUESTO = "presupuesto"

class ComprobanteStatus(enum.Enum):
    PENDIENTE = "pendiente"
    PROCESADO = "procesado"
    VALIDADO = "validado"
    RECHAZADO = "rechazado"
    ARCHIVADO = "archivado"

class VencimientoType(enum.Enum):
    IMPUESTO = "impuesto"
    SERVICIO = "servicio"
    ALQUILER = "alquiler"
    PROVEEDOR = "proveedor"
    CREDITO = "credito"
    SEGURO = "seguro"
    OTRO = "otro"

class VencimientoStatus(enum.Enum):
    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    VENCIDO = "vencido"
    CANCELADO = "cancelado"

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

class Comprobante(Base):
    __tablename__ = "comprobantes"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    business_id = Column(GUID(), ForeignKey("businesses.id"), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    
    tipo = Column(Enum(ComprobanteType), nullable=False)
    numero = Column(String, nullable=False, index=True)
    fecha_emision = Column(DateTime(timezone=True), nullable=False)
    fecha_vencimiento = Column(DateTime(timezone=True))
    
    cuit_emisor = Column(String(11), index=True)
    razon_social_emisor = Column(String)
    
    subtotal = Column(Float, nullable=False, default=0)
    iva = Column(Float, default=0)
    total = Column(Float, nullable=False)
    moneda = Column(String, default="ARS")
    
    status = Column(Enum(ComprobanteStatus), default=ComprobanteStatus.PENDIENTE)
    
    file_path = Column(String)
    file_url = Column(String)
    ocr_data = Column(Text)
    
    notas = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    business = relationship("Business")
    user = relationship("User")

class Vencimiento(Base):
    __tablename__ = "vencimientos"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    business_id = Column(GUID(), ForeignKey("businesses.id"), nullable=False)
    comprobante_id = Column(GUID(), ForeignKey("comprobantes.id"), nullable=True)
    
    tipo = Column(Enum(VencimientoType), nullable=False)
    descripcion = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    moneda = Column(String, default="ARS")
    
    fecha_vencimiento = Column(DateTime(timezone=True), nullable=False, index=True)
    fecha_pago = Column(DateTime(timezone=True))
    
    status = Column(Enum(VencimientoStatus), default=VencimientoStatus.PENDIENTE, index=True)
    
    recordatorio_dias_antes = Column(Integer, default=7)
    notificacion_enviada = Column(Boolean, default=False)
    
    notas = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    business = relationship("Business")
    comprobante = relationship("Comprobante")

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
    payment_metadata = Column(Text)
    webhook_data = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    order = relationship("Order", back_populates="payments")
    user = relationship("User")
    business = relationship("Business")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    business_id = Column(GUID(), ForeignKey("businesses.id"), nullable=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0)
    model = Column(String, default="gpt-4")
    chat_metadata = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")
    business = relationship("Business")

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
                "date": stat.date.isoformat() if hasattr(stat.date, 'isoformat') else str(stat.date),
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

class ComprobanteCRUD:
    """CRUD operations for Comprobante model."""
    
    @staticmethod
    def create(db, comprobante_data):
        """Create a new comprobante."""
        db_comprobante = Comprobante(**comprobante_data)
        db.add(db_comprobante)
        db.commit()
        db.refresh(db_comprobante)
        return db_comprobante
    
    @staticmethod
    def get_by_id(db, comprobante_id):
        """Get comprobante by ID."""
        return db.query(Comprobante).filter(Comprobante.id == comprobante_id).first()
    
    @staticmethod
    def get_by_business(db, business_id, skip=0, limit=100):
        """Get all comprobantes for a business."""
        return db.query(Comprobante).filter(
            Comprobante.business_id == business_id
        ).order_by(Comprobante.fecha_emision.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_numero(db, business_id, numero):
        """Get comprobante by numero."""
        return db.query(Comprobante).filter(
            Comprobante.business_id == business_id,
            Comprobante.numero == numero
        ).first()
    
    @staticmethod
    def get_by_status(db, business_id, status, skip=0, limit=100):
        """Get comprobantes by status."""
        return db.query(Comprobante).filter(
            Comprobante.business_id == business_id,
            Comprobante.status == status
        ).order_by(Comprobante.fecha_emision.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_date_range(db, business_id, fecha_inicio, fecha_fin, skip=0, limit=100):
        """Get comprobantes by date range."""
        return db.query(Comprobante).filter(
            Comprobante.business_id == business_id,
            Comprobante.fecha_emision >= fecha_inicio,
            Comprobante.fecha_emision <= fecha_fin
        ).order_by(Comprobante.fecha_emision.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db, comprobante_id, update_data):
        """Update comprobante."""
        db_comprobante = db.query(Comprobante).filter(Comprobante.id == comprobante_id).first()
        if db_comprobante:
            for field, value in update_data.items():
                setattr(db_comprobante, field, value)
            db.commit()
            db.refresh(db_comprobante)
        return db_comprobante
    
    @staticmethod
    def update_status(db, comprobante_id, status):
        """Update comprobante status."""
        db_comprobante = db.query(Comprobante).filter(Comprobante.id == comprobante_id).first()
        if db_comprobante:
            db_comprobante.status = status
            db.commit()
            db.refresh(db_comprobante)
        return db_comprobante
    
    @staticmethod
    def delete(db, comprobante_id):
        """Delete comprobante."""
        db_comprobante = db.query(Comprobante).filter(Comprobante.id == comprobante_id).first()
        if db_comprobante:
            db.delete(db_comprobante)
            db.commit()
        return True

class VencimientoCRUD:
    """CRUD operations for Vencimiento model."""
    
    @staticmethod
    def create(db, vencimiento_data):
        """Create a new vencimiento."""
        db_vencimiento = Vencimiento(**vencimiento_data)
        db.add(db_vencimiento)
        db.commit()
        db.refresh(db_vencimiento)
        return db_vencimiento
    
    @staticmethod
    def get_by_id(db, vencimiento_id):
        """Get vencimiento by ID."""
        return db.query(Vencimiento).filter(Vencimiento.id == vencimiento_id).first()
    
    @staticmethod
    def get_by_business(db, business_id, skip=0, limit=100):
        """Get all vencimientos for a business."""
        return db.query(Vencimiento).filter(
            Vencimiento.business_id == business_id
        ).order_by(Vencimiento.fecha_vencimiento.asc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_status(db, business_id, status, skip=0, limit=100):
        """Get vencimientos by status."""
        return db.query(Vencimiento).filter(
            Vencimiento.business_id == business_id,
            Vencimiento.status == status
        ).order_by(Vencimiento.fecha_vencimiento.asc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_proximos(db, business_id, dias=30):
        """Get vencimientos próximos (próximos N días)."""
        from datetime import datetime, timedelta
        hoy = datetime.now()
        fecha_limite = hoy + timedelta(days=dias)
        
        return db.query(Vencimiento).filter(
            Vencimiento.business_id == business_id,
            Vencimiento.status == VencimientoStatus.PENDIENTE,
            Vencimiento.fecha_vencimiento >= hoy,
            Vencimiento.fecha_vencimiento <= fecha_limite
        ).order_by(Vencimiento.fecha_vencimiento.asc()).all()
    
    @staticmethod
    def get_vencidos(db, business_id):
        """Get vencimientos vencidos."""
        from datetime import datetime
        hoy = datetime.now()
        
        return db.query(Vencimiento).filter(
            Vencimiento.business_id == business_id,
            Vencimiento.status == VencimientoStatus.PENDIENTE,
            Vencimiento.fecha_vencimiento < hoy
        ).order_by(Vencimiento.fecha_vencimiento.desc()).all()
    
    @staticmethod
    def get_by_date_range(db, business_id, fecha_inicio, fecha_fin, skip=0, limit=100):
        """Get vencimientos by date range."""
        return db.query(Vencimiento).filter(
            Vencimiento.business_id == business_id,
            Vencimiento.fecha_vencimiento >= fecha_inicio,
            Vencimiento.fecha_vencimiento <= fecha_fin
        ).order_by(Vencimiento.fecha_vencimiento.asc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db, vencimiento_id, update_data):
        """Update vencimiento."""
        db_vencimiento = db.query(Vencimiento).filter(Vencimiento.id == vencimiento_id).first()
        if db_vencimiento:
            for field, value in update_data.items():
                setattr(db_vencimiento, field, value)
            db.commit()
            db.refresh(db_vencimiento)
        return db_vencimiento
    
    @staticmethod
    def marcar_pagado(db, vencimiento_id, fecha_pago=None):
        """Marcar vencimiento como pagado."""
        from datetime import datetime
        db_vencimiento = db.query(Vencimiento).filter(Vencimiento.id == vencimiento_id).first()
        if db_vencimiento:
            db_vencimiento.status = VencimientoStatus.PAGADO
            db_vencimiento.fecha_pago = fecha_pago or datetime.now()
            db.commit()
            db.refresh(db_vencimiento)
        return db_vencimiento
    
    @staticmethod
    def delete(db, vencimiento_id):
        """Delete vencimiento."""
        db_vencimiento = db.query(Vencimiento).filter(Vencimiento.id == vencimiento_id).first()
        if db_vencimiento:
            db.delete(db_vencimiento)
            db.commit()
        return True

class ChatHistoryCRUD:
    """CRUD operations for ChatHistory model."""
    
    @staticmethod
    def create(db, chat_data):
        """Create a new chat history entry."""
        db_chat = ChatHistory(**chat_data)
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        return db_chat
    
    @staticmethod
    def get_by_id(db, chat_id):
        """Get chat entry by ID."""
        return db.query(ChatHistory).filter(ChatHistory.id == chat_id).first()
    
    @staticmethod
    def get_user_history(db, user_id, limit=50, skip=0):
        """Get chat history for a user."""
        return db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_conversation(db, user_id, limit=20):
        """Get recent conversation for context."""
        chats = db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.created_at.desc()).limit(limit).all()
        
        return list(reversed(chats))
    
    @staticmethod
    def delete_user_history(db, user_id):
        """Delete all chat history for a user."""
        db.query(ChatHistory).filter(ChatHistory.user_id == user_id).delete()
        db.commit()
        return True
    
    @staticmethod
    def get_business_history(db, business_id, limit=100, skip=0):
        """Get chat history for a business."""
        return db.query(ChatHistory).filter(
            ChatHistory.business_id == business_id
        ).order_by(ChatHistory.created_at.desc()).offset(skip).limit(limit).all()


class AIAuditLog(Base):
    __tablename__ = "ai_audit_logs"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    business_id = Column(GUID(), ForeignKey("businesses.id"), nullable=True)
    model_name = Column(String(100), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0)
    response_time_ms = Column(Integer, default=0)
    endpoint = Column(String(200), nullable=True)
    status = Column(String(50), default="success")
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    user = relationship("User")
    business = relationship("Business")


class AIAuditLogCRUD:
    
    @staticmethod
    def create(db, log_data):
        db_log = AIAuditLog(**log_data)
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    
    @staticmethod
    def get_by_business(db, business_id, skip=0, limit=100):
        return db.query(AIAuditLog).filter(
            AIAuditLog.business_id == business_id
        ).order_by(AIAuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_user(db, user_id, skip=0, limit=100):
        return db.query(AIAuditLog).filter(
            AIAuditLog.user_id == user_id
        ).order_by(AIAuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_usage_stats(db, business_id=None, user_id=None):
        from sqlalchemy import func
        
        query = db.query(
            func.count(AIAuditLog.id).label('total_requests'),
            func.sum(AIAuditLog.tokens_used).label('total_tokens'),
            func.avg(AIAuditLog.response_time_ms).label('avg_response_time')
        )
        
        if business_id:
            query = query.filter(AIAuditLog.business_id == business_id)
        if user_id:
            query = query.filter(AIAuditLog.user_id == user_id)
        
        result = query.first()
        return {
            "total_requests": result.total_requests or 0,
            "total_tokens": result.total_tokens or 0,
            "avg_response_time": float(result.avg_response_time or 0)
        }
    
