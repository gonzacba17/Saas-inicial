"""
Payment management endpoints with MercadoPago integration and role-based access control.
"""
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
import json
import hmac
import hashlib

from app.core.config import settings
from app.db.db import (
    get_db, Payment, PaymentCRUD, PaymentStatus, Order, OrderCRUD,
    Business, UserBusinessCRUD, UserBusinessRole
)
from app.schemas import (
    Payment as PaymentSchema, PaymentPreference, PaymentPreferenceRequest, PaymentWebhookData,
    User as UserSchema
)
from app.api.v1.auth import get_current_user
from app.services_directory.payment_service import payment_service

router = APIRouter()

def check_payment_permission(
    payment_id: UUID,
    current_user: UserSchema,
    db: Session,
    required_roles: Optional[List[UserBusinessRole]] = None
) -> bool:
    """Check if user has permission to access payment."""
    payment = PaymentCRUD.get_by_id(db, payment_id)
    if not payment:
        return False
    
    # Payment owners can always access their payments
    if payment.user_id == current_user.id:
        return True
    
    # Business owners/managers can access payments for their business
    if required_roles is None:
        required_roles = [UserBusinessRole.owner, UserBusinessRole.manager]
    
    return UserBusinessCRUD.has_permission(db, current_user.id, payment.business_id, required_roles)

def require_payment_permission(
    payment_id: UUID,
    current_user: UserSchema,
    db: Session,
    required_roles: Optional[List[UserBusinessRole]] = None
):
    """Raise HTTPException if user doesn't have permission to access payment."""
    if not check_payment_permission(payment_id, current_user, db, required_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this payment"
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

def verify_webhook_signature(request_body: bytes, signature: str) -> bool:
    """Verify MercadoPago webhook signature for security."""
    from app.core.security import get_webhook_secret
    
    webhook_secret = get_webhook_secret()
    
    # SECURITY: Webhook secret is MANDATORY in production
    environment = os.getenv("ENVIRONMENT", "development")
    if not webhook_secret:
        if environment == "production":
            logger.critical("Webhook signature validation failed: No webhook secret configured in production")
            return False
        else:
            logger.warning("Webhook signature validation skipped: No webhook secret configured in development")
            return True
    
    if not signature:
        logger.warning("Webhook signature validation failed: No signature provided")
        return False
    
    try:
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            request_body,
            hashlib.sha256
        ).hexdigest()
        
        # Use constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        if not is_valid:
            logger.warning("Webhook signature validation failed: Signature mismatch")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Webhook signature validation error: {str(e)}")
        return False

# ========================================
# PAYMENT ENDPOINTS
# ========================================

@router.get("/", response_model=List[PaymentSchema])
def list_user_payments(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """List current user's payments."""
    payments = PaymentCRUD.get_user_payments(db, current_user.id, skip=skip, limit=limit)
    return payments

@router.get("/business/{business_id}", response_model=List[PaymentSchema])
def list_business_payments(
    business_id: UUID,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """List payments for a specific business (business owners/managers only)."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Check if business exists
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            logger.warning(f"Business not found: {business_id}")
            raise HTTPException(status_code=404, detail="Business not found")
        
        # Check permissions
        require_business_permission(business_id, current_user, db)
        
        # Get payments - this should always return a list (empty if no payments)
        payments = PaymentCRUD.get_business_payments(db, business_id, skip=skip, limit=limit)
        
        # Ensure we always return a list
        if payments is None:
            logger.info(f"No payments found for business {business_id}, returning empty list")
            payments = []
        
        logger.info(f"Retrieved {len(payments)} payments for business {business_id}")
        return payments
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error retrieving payments for business {business_id}: {str(e)}")
        # Return empty list instead of 500 error when database query fails
        return []

@router.post("/create-preference", response_model=Dict[str, Any])
def create_payment_preference(
    payment_request: PaymentPreferenceRequest,
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Create MercadoPago payment preference for an order."""
    # Check if order exists and belongs to user
    order = OrderCRUD.get_by_id(db, payment_request.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create payment for this order"
        )
    
    # Check if payment already exists for this order
    existing_payment = PaymentCRUD.get_by_external_reference(db, str(order.id))
    if existing_payment and existing_payment.status not in [PaymentStatus.CANCELLED, PaymentStatus.REJECTED]:
        raise HTTPException(
            status_code=400, 
            detail="Payment already exists for this order"
        )
    
    try:
        # Check if we're in test/development mode
        if settings.environment in ["testing", "development"] or not hasattr(settings, 'mercadopago_access_token') or not settings.mercadopago_access_token:
            # Return mock payment preference for testing
            mock_payment_data = {
                "order_id": order.id,
                "user_id": current_user.id,
                "business_id": order.business_id,
                "preference_id": f"mock-preference-{order.id}",
                "external_reference": str(order.id),
                "amount": order.total_amount,
                "currency": "ARS",
                "status": PaymentStatus.PENDING,
                "metadata": json.dumps({"mock": True, "test_mode": True})
            }
            
            payment = PaymentCRUD.create(db, mock_payment_data)
            
            return {
                "payment_id": str(payment.id),
                "preference_id": f"mock-preference-{order.id}",
                "init_point": f"https://sandbox.mercadopago.com/checkout/v1/redirect?pref_id=mock-preference-{order.id}",
                "sandbox_init_point": f"https://sandbox.mercadopago.com/checkout/v1/redirect?pref_id=mock-preference-{order.id}",
                "order_id": str(order.id),
                "amount": order.total_amount,
                "mock": True,
                "message": "Mock payment preference created for testing"
            }
        
        # Production MercadoPago integration
        preference_data = payment_service.create_payment_preference(
            order_id=str(order.id),
            amount=order.total_amount,
            description=f"Order #{order.id} - {order.business.name}",
            payer_email=current_user.email
        )
        
        # Create payment record
        payment_data = {
            "order_id": order.id,
            "user_id": current_user.id,
            "business_id": order.business_id,
            "preference_id": preference_data["id"],
            "external_reference": str(order.id),
            "amount": order.total_amount,
            "currency": "ARS",
            "status": PaymentStatus.PENDING,
            "metadata": json.dumps({"mp_preference": preference_data})
        }
        
        payment = PaymentCRUD.create(db, payment_data)
        
        return {
            "payment_id": str(payment.id),
            "preference_id": preference_data["id"],
            "init_point": preference_data["init_point"],
            "sandbox_init_point": preference_data.get("sandbox_init_point"),
            "order_id": str(order.id),
            "amount": order.total_amount
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Convert service errors to 502 Bad Gateway (external service issue)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Payment service unavailable: {str(e)}"
        )

@router.get("/{payment_id}", response_model=PaymentSchema)
def get_payment(
    payment_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get payment by ID."""
    payment = PaymentCRUD.get_by_id(db, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check permissions
    require_payment_permission(payment_id, current_user, db)
    
    return payment

@router.get("/order/{order_id}", response_model=List[PaymentSchema])
def get_order_payments(
    order_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Get all payments for an order."""
    order = OrderCRUD.get_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user can access this order
    if order.user_id != current_user.id:
        # Check if user has business permissions
        if not check_business_permission(order.business_id, current_user, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access payments for this order"
            )
    
    payments = PaymentCRUD.get_by_order_id(db, order_id)
    return payments

@router.post("/webhook")
async def payment_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle MercadoPago payment webhook notifications."""
    try:
        # Get request body and signature
        body = await request.body()
        signature = request.headers.get("x-signature")
        
        # SECURITY: Mandatory webhook signature verification
        if not verify_webhook_signature(body, signature or ""):
            logger.warning(f"Webhook signature validation failed for payment webhook")
            raise HTTPException(
                status_code=401, 
                detail="Webhook signature validation failed"
            )
        
        # Parse webhook data
        webhook_data = json.loads(body.decode())
        
        # Handle different webhook types
        if webhook_data.get("type") == "payment":
            payment_id = webhook_data.get("data", {}).get("id")
            if not payment_id:
                raise HTTPException(status_code=400, detail="Missing payment ID in webhook")
            
            # Get payment details from MercadoPago
            try:
                mp_payment = payment_service.get_payment_details(payment_id)
                
                # Find our payment record by external reference
                external_reference = mp_payment.get("external_reference")
                if external_reference:
                    payment = PaymentCRUD.get_by_external_reference(db, external_reference)
                    if payment:
                        # Update payment status
                        new_status = payment_service.map_mercadopago_status(
                            mp_payment.get("status")
                        )
                        
                        update_data = {
                            "mercadopago_payment_id": str(payment_id),
                            "status": new_status,
                            "payment_method": mp_payment.get("payment_method_id"),
                            "payment_type": mp_payment.get("payment_type_id"),
                            "transaction_amount": mp_payment.get("transaction_amount"),
                            "net_received_amount": mp_payment.get("transaction_details", {}).get("net_received_amount"),
                            "webhook_data": json.dumps(webhook_data)
                        }
                        
                        PaymentCRUD.update_status(db, payment.id, new_status, update_data)
                        
                        # Update order status if payment is approved
                        if new_status == PaymentStatus.APPROVED:
                            OrderCRUD.update_status(db, payment.order_id, "confirmed")
                
            except Exception as e:
                # Log error but don't fail the webhook
                print(f"Error processing payment webhook: {str(e)}")
        
        return {"status": "ok"}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in webhook")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")

@router.post("/status/{payment_id}")
def check_payment_status(
    payment_id: UUID,
    db: Session = Depends(get_db), 
    current_user: UserSchema = Depends(get_current_user)
):
    """Manually check and update payment status from MercadoPago."""
    payment = PaymentCRUD.get_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check permissions
    require_payment_permission(payment_id, current_user, db)
    
    if not payment.mercadopago_payment_id:
        raise HTTPException(
            status_code=400, 
            detail="Payment does not have MercadoPago ID"
        )
    
    try:
        # Get latest payment status from MercadoPago
        mp_payment = payment_service.get_payment_details(payment.mercadopago_payment_id)
        
        # Update local payment status
        new_status = payment_service.map_mercadopago_status(
            mp_payment.get("status")
        )
        
        update_data = {
            "status": new_status,
            "payment_method": mp_payment.get("payment_method_id"),
            "payment_type": mp_payment.get("payment_type_id"),
            "transaction_amount": mp_payment.get("transaction_amount"),
            "net_received_amount": mp_payment.get("transaction_details", {}).get("net_received_amount")
        }
        
        updated_payment = PaymentCRUD.update_status(db, payment_id, new_status, update_data)
        
        return {
            "payment_id": str(payment_id),
            "status": new_status,
            "mercadopago_status": mp_payment.get("status"),
            "updated": True
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Convert service errors to 502 Bad Gateway (external service issue)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Payment service unavailable: {str(e)}"
        )
