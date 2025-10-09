"""
Unified Pydantic schemas for all models.
All data validation and serialization schemas consolidated in one file for simplicity.
"""
from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum
from app.middleware.validation import (
    StrictValidationMixin, validate_business_name, validate_product_name, 
    validate_price, validate_description, validate_password, InputSanitizer
)

# ========================================
# TOKEN SCHEMAS
# ========================================

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: Optional[str] = None
    role: Optional[str] = None

class TokenData(BaseModel):
    username: Optional[str] = None

# ========================================
# USER SCHEMAS
# ========================================

class UserBase(BaseModel, StrictValidationMixin):
    email: EmailStr
    username: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return InputSanitizer.validate_email(v)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        v = InputSanitizer.sanitize_string(v, max_length=50)
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Username can only contain letters, numbers, hyphens and underscores")
        return v

class UserCreate(UserBase):
    password: str
    role: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        return validate_password(v)
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v is None:
            return "user"  # Default role
        valid_roles = ["user", "owner", "admin"]
        if v.lower() not in valid_roles:
            raise ValueError(f"Invalid role: {v}. Must be one of {valid_roles}")
        return v.lower()

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDBBase(UserBase):
    id: UUID
    role: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True

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
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate and sanitize business name."""
        if not v or not v.strip():
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business name is required and cannot be empty"
            )
        return InputSanitizer.sanitize_string(v, max_length=100)
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate and sanitize business description."""
        if v is not None:
            return InputSanitizer.sanitize_string(v, max_length=500)
        return v
    
    @field_validator('address')
    @classmethod
    def validate_address(cls, v):
        """Validate and sanitize business address."""
        if v is not None:
            return InputSanitizer.sanitize_string(v, max_length=200)
        return v

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
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate and sanitize business name."""
        if v is not None:
            if not v.strip():
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Business name cannot be empty"
                )
            return InputSanitizer.sanitize_string(v, max_length=100)
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate and sanitize business description."""
        if v is not None:
            return InputSanitizer.sanitize_string(v, max_length=500)
        return v
    
    @field_validator('address')
    @classmethod
    def validate_address(cls, v):
        """Validate and sanitize business address."""
        if v is not None:
            return InputSanitizer.sanitize_string(v, max_length=200)
        return v

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

class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int
    unit_price: Optional[float] = None

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

# ========================================
# USER BUSINESS SCHEMAS
# ========================================

class UserBusinessRole(str, Enum):
    OWNER = "owner"
    MANAGER = "manager"
    EMPLOYEE = "employee"

class UserBusinessBase(BaseModel):
    role: UserBusinessRole = UserBusinessRole.OWNER

class UserBusinessCreate(UserBusinessBase):
    business_id: UUID

class UserBusinessUpdate(BaseModel):
    role: Optional[UserBusinessRole] = None
    is_active: Optional[bool] = None

class UserBusinessInDBBase(UserBusinessBase):
    id: UUID
    user_id: UUID
    business_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserBusiness(UserBusinessInDBBase):
    pass

class UserBusinessInDB(UserBusinessInDBBase):
    pass

# ========================================
# ANALYTICS SCHEMAS
# ========================================

class ProductSalesStats(BaseModel):
    product_id: UUID
    product_name: str
    total_quantity: int
    total_revenue: float

class BusinessAnalytics(BaseModel):
    business_id: UUID
    business_name: str
    total_orders: int
    total_revenue: float
    pending_orders: int
    completed_orders: int
    top_products: list[ProductSalesStats]

class DateRangeStats(BaseModel):
    start_date: datetime
    end_date: datetime
    total_orders: int
    total_revenue: float
    average_order_value: float

# ========================================
# AI ASSISTANT SCHEMAS
# ========================================

class AIAssistantType(str, Enum):
    PRODUCT_SUGGESTION = "product_suggestion"
    SALES_ANALYSIS = "sales_analysis"
    BUSINESS_INSIGHTS = "business_insights"
    GENERAL_QUERY = "general_query"

class AIQueryRequest(BaseModel):
    prompt: str
    assistant_type: AIAssistantType
    business_id: Optional[UUID] = None

class AIConversationBase(BaseModel):
    prompt: str
    response: str
    assistant_type: AIAssistantType
    business_id: Optional[UUID] = None
    tokens_used: Optional[int] = 0
    response_time_ms: Optional[int] = 0

class AIConversationCreate(AIConversationBase):
    pass

class AIConversationInDBBase(AIConversationBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class AIConversation(AIConversationInDBBase):
    pass

class AIConversationInDB(AIConversationInDBBase):
    pass

class AIUsageStats(BaseModel):
    total_conversations: int
    total_tokens: int
    avg_response_time: float

class AIResponse(BaseModel):
    response: str
    conversation_id: UUID
    tokens_used: int
    response_time_ms: int

# ========================================
# PAYMENT SCHEMAS
# ========================================

class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    AUTHORIZED = "authorized"
    IN_PROCESS = "in_process"
    IN_MEDIATION = "in_mediation"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    CHARGED_BACK = "charged_back"

class PaymentBase(BaseModel):
    order_id: UUID
    amount: float
    currency: str = "ARS"

class PaymentCreate(PaymentBase):
    user_id: UUID
    business_id: UUID
    external_reference: Optional[str] = None

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatusEnum] = None
    mercadopago_payment_id: Optional[str] = None
    payment_method: Optional[str] = None
    payment_type: Optional[str] = None
    transaction_amount: Optional[float] = None
    net_received_amount: Optional[float] = None
    total_paid_amount: Optional[float] = None
    metadata: Optional[str] = None
    webhook_data: Optional[str] = None

class PaymentInDBBase(PaymentBase):
    id: UUID
    user_id: UUID
    business_id: UUID
    mercadopago_payment_id: Optional[str] = None
    preference_id: Optional[str] = None
    external_reference: Optional[str] = None
    status: PaymentStatusEnum
    payment_method: Optional[str] = None
    payment_type: Optional[str] = None
    transaction_amount: Optional[float] = None
    net_received_amount: Optional[float] = None
    total_paid_amount: Optional[float] = None
    metadata: Optional[str] = Field(None, alias="payment_metadata")
    webhook_data: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True
        populate_by_name = True

class Payment(PaymentInDBBase):
    pass

class PaymentInDB(PaymentInDBBase):
    pass

class PaymentPreferenceRequest(BaseModel):
    order_id: UUID

class PaymentPreference(BaseModel):
    success: bool
    preference_id: Optional[str] = None
    checkout_url: Optional[str] = None
    sandbox_checkout_url: Optional[str] = None
    total_amount: float
    mock: Optional[bool] = False
    message: Optional[str] = None
    error: Optional[str] = None

class PaymentWebhookData(BaseModel):
    action: str
    api_version: str
    data: dict
    date_created: str
    id: int
    live_mode: bool
    type: str
    user_id: str

# ========================================
# COMPROBANTE SCHEMAS
# ========================================

class ComprobanteTypeEnum(str, Enum):
    FACTURA_A = "factura_a"
    FACTURA_B = "factura_b"
    FACTURA_C = "factura_c"
    NOTA_CREDITO = "nota_credito"
    NOTA_DEBITO = "nota_debito"
    RECIBO = "recibo"
    PRESUPUESTO = "presupuesto"

class ComprobanteStatusEnum(str, Enum):
    PENDIENTE = "pendiente"
    PROCESADO = "procesado"
    VALIDADO = "validado"
    RECHAZADO = "rechazado"
    ARCHIVADO = "archivado"

class ComprobanteBase(BaseModel):
    tipo: ComprobanteTypeEnum
    numero: str
    fecha_emision: datetime
    fecha_vencimiento: Optional[datetime] = None
    cuit_emisor: Optional[str] = None
    razon_social_emisor: Optional[str] = None
    subtotal: float = 0
    iva: float = 0
    total: float
    moneda: str = "ARS"
    notas: Optional[str] = None
    
    @field_validator('numero')
    @classmethod
    def validate_numero(cls, v):
        if not v or len(v) < 3:
            raise ValueError("Número de comprobante debe tener al menos 3 caracteres")
        return v
    
    @field_validator('cuit_emisor')
    @classmethod
    def validate_cuit(cls, v):
        if v is not None:
            v = v.replace("-", "").replace(" ", "")
            if len(v) != 11 or not v.isdigit():
                raise ValueError("CUIT debe tener 11 dígitos")
        return v
    
    @field_validator('total')
    @classmethod
    def validate_total(cls, v):
        if v < 0:
            raise ValueError("Total no puede ser negativo")
        return v

class ComprobanteCreate(ComprobanteBase):
    business_id: UUID

class ComprobanteUpdate(BaseModel):
    tipo: Optional[ComprobanteTypeEnum] = None
    numero: Optional[str] = None
    fecha_emision: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None
    cuit_emisor: Optional[str] = None
    razon_social_emisor: Optional[str] = None
    subtotal: Optional[float] = None
    iva: Optional[float] = None
    total: Optional[float] = None
    moneda: Optional[str] = None
    status: Optional[ComprobanteStatusEnum] = None
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    ocr_data: Optional[str] = None
    notas: Optional[str] = None

class ComprobanteInDBBase(ComprobanteBase):
    id: UUID
    business_id: UUID
    user_id: UUID
    status: ComprobanteStatusEnum
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    ocr_data: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True

class Comprobante(ComprobanteInDBBase):
    pass

class ComprobanteInDB(ComprobanteInDBBase):
    pass

# ========================================
# VENCIMIENTO SCHEMAS
# ========================================

class VencimientoTypeEnum(str, Enum):
    IMPUESTO = "impuesto"
    SERVICIO = "servicio"
    ALQUILER = "alquiler"
    PROVEEDOR = "proveedor"
    CREDITO = "credito"
    SEGURO = "seguro"
    OTRO = "otro"

class VencimientoStatusEnum(str, Enum):
    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    VENCIDO = "vencido"
    CANCELADO = "cancelado"

class VencimientoBase(BaseModel):
    tipo: VencimientoTypeEnum
    descripcion: str
    monto: float
    moneda: str = "ARS"
    fecha_vencimiento: datetime
    recordatorio_dias_antes: int = 7
    notas: Optional[str] = None
    
    @field_validator('descripcion')
    @classmethod
    def validate_descripcion(cls, v):
        if not v or len(v) < 3:
            raise ValueError("Descripción debe tener al menos 3 caracteres")
        return v
    
    @field_validator('monto')
    @classmethod
    def validate_monto(cls, v):
        if v < 0:
            raise ValueError("Monto no puede ser negativo")
        return v
    
    @field_validator('recordatorio_dias_antes')
    @classmethod
    def validate_recordatorio(cls, v):
        if v < 0 or v > 365:
            raise ValueError("Recordatorio debe estar entre 0 y 365 días")
        return v

class VencimientoCreate(VencimientoBase):
    business_id: UUID
    comprobante_id: Optional[UUID] = None

class VencimientoUpdate(BaseModel):
    tipo: Optional[VencimientoTypeEnum] = None
    descripcion: Optional[str] = None
    monto: Optional[float] = None
    moneda: Optional[str] = None
    fecha_vencimiento: Optional[datetime] = None
    fecha_pago: Optional[datetime] = None
    status: Optional[VencimientoStatusEnum] = None
    recordatorio_dias_antes: Optional[int] = None
    notificacion_enviada: Optional[bool] = None
    notas: Optional[str] = None

class VencimientoInDBBase(VencimientoBase):
    id: UUID
    business_id: UUID
    comprobante_id: Optional[UUID] = None
    fecha_pago: Optional[datetime] = None
    status: VencimientoStatusEnum
    notificacion_enviada: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True

class Vencimiento(VencimientoInDBBase):
    pass

class VencimientoInDB(VencimientoInDBBase):
    pass

# ========================================
# OCR SCHEMAS
# ========================================

class OCRExtractedData(BaseModel):
    success: bool
    tipo: Optional[str] = None
    numero: Optional[str] = None
    fecha_emision: Optional[str] = None
    total: Optional[float] = None
    subtotal: Optional[float] = None
    iva: Optional[float] = None
    cuit_emisor: Optional[str] = None
    razon_social: Optional[str] = None
    confidence: Optional[float] = None
    raw_text: Optional[str] = None
    file_format: Optional[str] = None
    error: Optional[str] = None
    mock: Optional[bool] = False
    message: Optional[str] = None

class OCRResponse(BaseModel):
    success: bool
    filename: str
    file_size: int
    processing_time: float
    data: OCRExtractedData
    saved_to_comprobante: bool = False
    comprobante_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class OCRUploadResponse(BaseModel):
    message: str
    ocr_result: OCRResponse

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    business_id: Optional[str] = None
    use_rag: bool = False
    collection_name: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    response: str
    user_id: Optional[str] = None
    timestamp: str
    tokens_used: Optional[Dict[str, int]] = None
    model: Optional[str] = None
    mock: bool = False
    message: Optional[str] = None

class ChatHistoryItem(BaseModel):
    id: str
    user_id: str
    business_id: Optional[str] = None
    role: str
    content: str
    tokens_used: int
    model: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    success: bool
    history: List[ChatHistoryItem]
    count: int

class AddDocumentRequest(BaseModel):
    text: str
    collection_name: str = "documents"
    metadata: Optional[Dict[str, Any]] = None
    business_id: Optional[str] = None

class AddDocumentResponse(BaseModel):
    success: bool
    document_ids: List[str]
    count: int
    collection: str
    mock: bool = False
    message: Optional[str] = None

class NotificationEventType(str, Enum):
    COMPROBANTE_CREATED = "comprobante_created"
    VENCIMIENTO_PROXIMO = "vencimiento_proximo"
    VENCIMIENTO_VENCIDO = "vencimiento_vencido"
    CHATBOT_INSIGHT = "chatbot_insight"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_REPORT = "weekly_report"
    SYSTEM_ALERT = "system_alert"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    PUSH = "push"
    BOTH = "both"

class NotificationEvent(BaseModel):
    event_type: NotificationEventType
    payload: Dict[str, Any]
    user_email: str
    user_id: str
    user_name: str
    channel: NotificationChannel = NotificationChannel.BOTH

class NotificationResponse(BaseModel):
    success: bool
    event_type: str
    user_id: str
    timestamp: str
    email_sent: bool
    push_sent: bool
    email_result: Optional[Dict[str, Any]] = None
    push_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class EmailTemplate(BaseModel):
    name: str
    subject: str
    description: str
    variables: List[str]

class TestNotificationRequest(BaseModel):
    recipient_email: str
    notification_type: NotificationEventType
    test_data: Optional[Dict[str, Any]] = None

class NotificationStatusResponse(BaseModel):
    email_service_available: bool
    push_service_available: bool
    celery_worker_active: bool
    templates_loaded: int
    message: str