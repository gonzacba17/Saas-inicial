from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.businesses import router as businesses_router
from app.api.v1.products import router as products_router
from app.api.v1.orders import router as orders_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.payments import router as payments_router
from app.api.v1.ai import router as ai_router
from app.api.v1.secrets import router as secrets_router
from app.api.v1.comprobantes import router as comprobantes_router
from app.api.v1.vencimientos import router as vencimientos_router
from app.api.v1.ocr import router as ocr_router
from app.api.v1.chatbot import router as chatbot_router
from app.api.v1.notifications import router as notifications_router

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# User management endpoints  
api_router.include_router(users_router, prefix="/users", tags=["users"])

# Business management endpoints
api_router.include_router(businesses_router, prefix="/businesses", tags=["businesses"])

# Product management endpoints
api_router.include_router(products_router, prefix="/products", tags=["products"])

# Order management endpoints
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])

# Analytics endpoints
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

# Payment endpoints
api_router.include_router(payments_router, prefix="/payments", tags=["payments"])

# AI assistant endpoints
api_router.include_router(ai_router, prefix="/ai", tags=["ai-assistant"])

# Secrets management endpoints (admin only)
api_router.include_router(secrets_router, prefix="/secrets", tags=["secrets"])

# Comprobantes (facturas, recibos) endpoints
api_router.include_router(comprobantes_router, prefix="/comprobantes", tags=["comprobantes"])

# Vencimientos (pagos pendientes) endpoints
api_router.include_router(vencimientos_router, prefix="/vencimientos", tags=["vencimientos"])

# OCR (invoice/receipt extraction) endpoints
api_router.include_router(ocr_router, prefix="/ocr", tags=["OCR"])

# Chatbot Advanced (LangChain + RAG) endpoints
api_router.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])

# Notifications (Email + Push + Celery) endpoints
api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])