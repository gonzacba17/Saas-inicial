"""
Payment service using MercadoPago SDK for handling payments.
Provides sandbox integration for testing and production ready functionality.
"""
import mercadopago
from typing import Dict, Any, Optional
from app.core.config import settings
import uuid
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    """MercadoPago payment service for handling transactions."""
    
    def __init__(self):
        """Initialize MercadoPago SDK with access token."""
        self.sdk = None
        if settings.mercadopago_key:
            self.sdk = mercadopago.SDK(settings.mercadopago_key)
            logger.info("MercadoPago SDK initialized successfully")
        else:
            logger.warning("MercadoPago access token not configured")
    
    def create_payment_preference(
        self,
        order_id: str,
        items: list,
        payer_email: str,
        back_urls: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a payment preference for MercadoPago checkout.
        
        Args:
            order_id: Internal order ID
            items: List of items with id, title, quantity, unit_price
            payer_email: Customer email
            back_urls: Optional URLs for success, failure, pending
            
        Returns:
            Dict with preference data including checkout URL
        """
        if not self.sdk:
            # Mock response for development when SDK is not configured
            return self._mock_payment_preference(order_id, items)
        
        try:
            # Default back URLs
            if not back_urls:
                base_url = "http://localhost:5173"  # Frontend URL
                back_urls = {
                    "success": f"{base_url}/payment/success",
                    "failure": f"{base_url}/payment/failure",
                    "pending": f"{base_url}/payment/pending"
                }
            
            # Calculate total
            total_amount = sum(item.get("unit_price", 0) * item.get("quantity", 1) for item in items)
            
            preference_data = {
                "items": [
                    {
                        "id": item.get("id"),
                        "title": item.get("title", "Product"),
                        "quantity": item.get("quantity", 1),
                        "unit_price": float(item.get("unit_price", 0)),
                        "currency_id": "ARS"  # Argentine Peso for MercadoPago
                    }
                    for item in items
                ],
                "payer": {
                    "email": payer_email
                },
                "back_urls": back_urls,
                "auto_return": "approved",
                "external_reference": order_id,
                "notification_url": f"http://localhost:8000/api/v1/payments/webhook",
                "metadata": {
                    "order_id": order_id
                }
            }
            
            response = self.sdk.preference().create(preference_data)
            
            if response["status"] == 201:
                preference = response["response"]
                return {
                    "success": True,
                    "preference_id": preference["id"],
                    "checkout_url": preference["init_point"],
                    "sandbox_checkout_url": preference["sandbox_init_point"],
                    "total_amount": total_amount
                }
            else:
                logger.error(f"MercadoPago preference creation failed: {response}")
                return {
                    "success": False,
                    "error": "Failed to create payment preference"
                }
                
        except Exception as e:
            logger.error(f"Error creating MercadoPago preference: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _mock_payment_preference(self, order_id: str, items: list) -> Dict[str, Any]:
        """
        Mock payment preference for development/testing.
        """
        total_amount = sum(item.get("unit_price", 0) * item.get("quantity", 1) for item in items)
        mock_preference_id = f"mock-{uuid.uuid4().hex[:8]}"
        
        return {
            "success": True,
            "preference_id": mock_preference_id,
            "checkout_url": f"http://localhost:5173/payment/mock/{mock_preference_id}",
            "sandbox_checkout_url": f"http://localhost:5173/payment/mock/{mock_preference_id}",
            "total_amount": total_amount,
            "mock": True,
            "message": "Mock payment for development - MercadoPago key not configured"
        }
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process MercadoPago webhook notification.
        
        Args:
            webhook_data: Webhook payload from MercadoPago
            
        Returns:
            Dict with processing result
        """
        if not self.sdk:
            return {
                "success": True,
                "mock": True,
                "message": "Mock webhook processing - MercadoPago not configured"
            }
        
        try:
            # Get payment ID from webhook
            payment_id = webhook_data.get("data", {}).get("id")
            
            if not payment_id:
                return {
                    "success": False,
                    "error": "No payment ID in webhook data"
                }
            
            # Get payment details from MercadoPago
            payment_response = self.sdk.payment().get(payment_id)
            
            if payment_response["status"] == 200:
                payment_data = payment_response["response"]
                
                return {
                    "success": True,
                    "payment_id": payment_id,
                    "status": payment_data.get("status"),
                    "external_reference": payment_data.get("external_reference"),
                    "amount": payment_data.get("transaction_amount"),
                    "payment_data": payment_data
                }
            else:
                logger.error(f"Failed to get payment details: {payment_response}")
                return {
                    "success": False,
                    "error": "Failed to retrieve payment details"
                }
                
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment status from MercadoPago.
        
        Args:
            payment_id: MercadoPago payment ID
            
        Returns:
            Dict with payment status information
        """
        if not self.sdk:
            return {
                "success": True,
                "status": "approved",
                "mock": True,
                "message": "Mock payment status - MercadoPago not configured"
            }
        
        try:
            response = self.sdk.payment().get(payment_id)
            
            if response["status"] == 200:
                payment_data = response["response"]
                return {
                    "success": True,
                    "status": payment_data.get("status"),
                    "amount": payment_data.get("transaction_amount"),
                    "external_reference": payment_data.get("external_reference"),
                    "payment_data": payment_data
                }
            else:
                return {
                    "success": False,
                    "error": "Payment not found"
                }
                
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Global payment service instance
payment_service = PaymentService()