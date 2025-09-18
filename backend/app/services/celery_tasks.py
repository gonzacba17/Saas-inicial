"""
Celery tasks for background processing.
Handles AI processing, notifications, reports, and other async operations.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from celery import Task
from sqlalchemy.orm import Session

from app.services.celery_app import celery_app
from app.db.db import get_db, AnalyticsCRUD, AIConversationCRUD, BusinessCRUD, UserCRUD
from app.services.ai_service import ai_service
from app.schemas import AIQueryRequest

# Set up logging
logger = logging.getLogger(__name__)

class DatabaseTask(Task):
    """Base task class that provides database session."""
    
    def __call__(self, *args, **kwargs):
        with next(get_db()) as db:
            return self.run(db, *args, **kwargs)
    
    def run(self, db: Session, *args, **kwargs):
        raise NotImplementedError

# ========================================
# AI PROCESSING TASKS
# ========================================

@celery_app.task(bind=True, base=DatabaseTask)
def generate_ai_insights(self, db: Session, user_id: str, business_id: str, prompt: str, assistant_type: str = "BUSINESS_INSIGHTS") -> Dict[str, Any]:
    """Generate AI insights in background."""
    try:
        from app.db.db import AIAssistantType
        
        # Map string to enum
        type_mapping = {
            "PRODUCT_SUGGESTION": AIAssistantType.PRODUCT_SUGGESTION,
            "SALES_ANALYSIS": AIAssistantType.SALES_ANALYSIS,
            "BUSINESS_INSIGHTS": AIAssistantType.BUSINESS_INSIGHTS,
            "GENERAL": AIAssistantType.GENERAL
        }
        
        ai_query = AIQueryRequest(
            prompt=prompt,
            business_id=business_id,
            assistant_type=type_mapping.get(assistant_type, AIAssistantType.BUSINESS_INSIGHTS)
        )
        
        # Process with AI service
        import asyncio
        result = asyncio.run(ai_service.process_query(db, user_id, ai_query))
        
        logger.info(f"Generated AI insights for user {user_id}, business {business_id}")
        return {
            "status": "success",
            "conversation_id": str(result["conversation_id"]),
            "tokens_used": result["tokens_used"],
            "response_time_ms": result["response_time_ms"]
        }
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@celery_app.task(bind=True, base=DatabaseTask)
def cleanup_old_ai_conversations(self, db: Session, days_old: int = 90) -> Dict[str, Any]:
    """Clean up AI conversations older than specified days."""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Delete old conversations
        deleted_count = AIConversationCRUD.delete_old_conversations(db, cutoff_date)
        
        logger.info(f"Cleaned up {deleted_count} old AI conversations")
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up AI conversations: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

# ========================================
# BUSINESS ANALYTICS TASKS
# ========================================

@celery_app.task(bind=True, base=DatabaseTask)
def generate_business_report(self, db: Session, business_id: str, report_type: str = "daily") -> Dict[str, Any]:
    """Generate comprehensive business report."""
    try:
        business = BusinessCRUD.get_by_id(db, business_id)
        if not business:
            return {"status": "error", "error": "Business not found"}
        
        # Get analytics data
        analytics = AnalyticsCRUD.get_business_analytics(db, business_id)
        daily_sales = AnalyticsCRUD.get_daily_sales(db, business_id, 30)
        
        # Generate report data
        report = {
            "business_id": business_id,
            "business_name": business.name,
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "analytics": analytics,
            "daily_sales": daily_sales,
            "insights": {
                "avg_daily_revenue": sum(d["revenue"] for d in daily_sales[-7:]) / 7 if len(daily_sales) >= 7 else 0,
                "growth_rate": _calculate_growth_rate(daily_sales),
                "top_performing_day": max(daily_sales, key=lambda x: x["revenue"])["date"] if daily_sales else None
            }
        }
        
        logger.info(f"Generated {report_type} report for business {business_id}")
        return {
            "status": "success",
            "report": report
        }
        
    except Exception as e:
        logger.error(f"Error generating business report: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@celery_app.task(bind=True, base=DatabaseTask)
def generate_daily_business_reports(self, db: Session) -> Dict[str, Any]:
    """Generate daily reports for all active businesses."""
    try:
        businesses = BusinessCRUD.get_all_active(db)
        reports_generated = 0
        
        for business in businesses:
            try:
                generate_business_report.delay(str(business.id), "daily")
                reports_generated += 1
            except Exception as e:
                logger.error(f"Error scheduling report for business {business.id}: {str(e)}")
        
        logger.info(f"Scheduled daily reports for {reports_generated} businesses")
        return {
            "status": "success",
            "reports_scheduled": reports_generated
        }
        
    except Exception as e:
        logger.error(f"Error generating daily business reports: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@celery_app.task(bind=True, base=DatabaseTask)
def update_analytics_cache(self, db: Session) -> Dict[str, Any]:
    """Update cached analytics data for faster API responses."""
    try:
        # This would update Redis cache with pre-computed analytics
        # For now, just log the operation
        businesses = BusinessCRUD.get_all_active(db)
        cached_businesses = 0
        
        for business in businesses:
            try:
                # Pre-compute analytics
                analytics = AnalyticsCRUD.get_business_analytics(db, str(business.id))
                # In a real implementation, this would be cached in Redis
                cached_businesses += 1
            except Exception as e:
                logger.error(f"Error caching analytics for business {business.id}: {str(e)}")
        
        logger.info(f"Updated analytics cache for {cached_businesses} businesses")
        return {
            "status": "success",
            "cached_businesses": cached_businesses
        }
        
    except Exception as e:
        logger.error(f"Error updating analytics cache: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

# ========================================
# NOTIFICATION TASKS
# ========================================

@celery_app.task(bind=True)
def send_notification(self, user_id: str, notification_type: str, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Send notification to user (email, push, SMS, etc.)."""
    try:
        # In a real implementation, this would integrate with notification services
        # like Firebase, SendGrid, Twilio, etc.
        
        logger.info(f"Sending {notification_type} notification to user {user_id}: {message}")
        
        # Simulate notification sending
        notification_data = {
            "user_id": user_id,
            "type": notification_type,
            "message": message,
            "data": data or {},
            "sent_at": datetime.utcnow().isoformat(),
            "status": "sent"
        }
        
        return {
            "status": "success",
            "notification": notification_data
        }
        
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@celery_app.task(bind=True)
def send_order_notification(self, order_id: str, notification_type: str) -> Dict[str, Any]:
    """Send order-related notifications."""
    try:
        with next(get_db()) as db:
            from app.db.db import OrderCRUD
            
            order = OrderCRUD.get_by_id(db, order_id)
            if not order:
                return {"status": "error", "error": "Order not found"}
            
            # Send notification to customer
            customer_message = _get_order_notification_message(order, notification_type, "customer")
            send_notification.delay(
                str(order.user_id),
                notification_type,
                customer_message,
                {"order_id": order_id}
            )
            
            # Send notification to business owner
            business_message = _get_order_notification_message(order, notification_type, "business")
            # In a real app, you'd get business owner user_id
            
            return {
                "status": "success",
                "order_id": order_id,
                "notifications_sent": 2
            }
            
    except Exception as e:
        logger.error(f"Error sending order notification: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

# ========================================
# PAYMENT PROCESSING TASKS
# ========================================

@celery_app.task(bind=True, base=DatabaseTask)
def process_payment_webhook(self, db: Session, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process MercadoPago webhook in background."""
    try:
        from app.services.payment_service import payment_service
        
        # Process the webhook
        result = payment_service.process_webhook(db, webhook_data)
        
        if result.get("order_updated"):
            # Send order status notification
            send_order_notification.delay(
                result["order_id"],
                "payment_status_update"
            )
        
        logger.info(f"Processed payment webhook for payment {result.get('payment_id')}")
        return {
            "status": "success",
            "payment_id": result.get("payment_id"),
            "order_updated": result.get("order_updated", False)
        }
        
    except Exception as e:
        logger.error(f"Error processing payment webhook: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

# ========================================
# UTILITY TASKS
# ========================================

@celery_app.task
def health_check() -> str:
    """Health check task for monitoring Celery workers."""
    return "healthy"

# ========================================
# HELPER FUNCTIONS
# ========================================

def _calculate_growth_rate(daily_sales: List[Dict]) -> float:
    """Calculate revenue growth rate from daily sales data."""
    if len(daily_sales) < 14:
        return 0.0
    
    # Compare last 7 days vs previous 7 days
    recent_week = sum(d["revenue"] for d in daily_sales[-7:])
    previous_week = sum(d["revenue"] for d in daily_sales[-14:-7])
    
    if previous_week == 0:
        return 100.0 if recent_week > 0 else 0.0
    
    return ((recent_week - previous_week) / previous_week) * 100

def _get_order_notification_message(order, notification_type: str, recipient: str) -> str:
    """Generate order notification message based on type and recipient."""
    messages = {
        "order_created": {
            "customer": f"Tu orden #{order.id} ha sido creada exitosamente. Total: ${order.total}",
            "business": f"Nueva orden recibida #{order.id}. Total: ${order.total}"
        },
        "order_confirmed": {
            "customer": f"Tu orden #{order.id} ha sido confirmada y está en preparación.",
            "business": f"Orden #{order.id} confirmada y en preparación."
        },
        "order_ready": {
            "customer": f"Tu orden #{order.id} está lista para recoger.",
            "business": f"Orden #{order.id} lista para entrega."
        },
        "payment_status_update": {
            "customer": f"El estado de pago de tu orden #{order.id} ha sido actualizado.",
            "business": f"Estado de pago actualizado para orden #{order.id}."
        }
    }
    
    return messages.get(notification_type, {}).get(recipient, "Actualización de orden")