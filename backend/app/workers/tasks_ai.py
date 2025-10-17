from celery import shared_task
from typing import Dict, Any, Optional
import time
from datetime import datetime
from app.core.celery_app import celery_app
from app.services_directory.ai_service import ai_service


@shared_task(bind=True, max_retries=3)
def generate_sales_report(self, business_id: str, period: str = "monthly") -> Dict[str, Any]:
    try:
        start_time = time.time()
        
        analysis = ai_service.get_sales_analysis(business_id=business_id)
        
        response_time = int((time.time() - start_time) * 1000)
        
        return {
            "status": "completed",
            "business_id": business_id,
            "period": period,
            "analysis": analysis.get("analysis", {}),
            "insights": analysis.get("insights", []),
            "recommendations": analysis.get("recommendations", []),
            "response_time_ms": response_time,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        self.retry(countdown=60, exc=e)


@shared_task(bind=True, max_retries=3)
def generate_product_recommendations(self, business_id: str, business_type: str, business_name: str) -> Dict[str, Any]:
    try:
        start_time = time.time()
        
        suggestions = ai_service.get_product_suggestions(
            business_id=business_id,
            business_type=business_type,
            business_name=business_name
        )
        
        response_time = int((time.time() - start_time) * 1000)
        
        return {
            "status": "completed",
            "business_id": business_id,
            "suggestions": suggestions.get("suggestions", []),
            "explanation": suggestions.get("response", ""),
            "response_time_ms": response_time,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        self.retry(countdown=60, exc=e)


@shared_task(bind=True, max_retries=3)
def analyze_customer_behavior(self, business_id: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        start_time = time.time()
        
        query_text = f"Analyze customer behavior patterns for business {business_id}"
        if customer_id:
            query_text += f" focusing on customer {customer_id}"
        
        response = ai_service.process_query(
            user_id="system",
            business_id=business_id,
            query_text=query_text,
            assistant_type="SALES_ANALYSIS"
        )
        
        response_time = int((time.time() - start_time) * 1000)
        
        return {
            "status": "completed",
            "business_id": business_id,
            "customer_id": customer_id,
            "analysis": response.get("response", ""),
            "response_time_ms": response_time,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        self.retry(countdown=60, exc=e)


@shared_task(bind=True, max_retries=3)
def generate_inventory_forecast(self, business_id: str, product_ids: list = None) -> Dict[str, Any]:
    try:
        start_time = time.time()
        
        query_text = f"Generate inventory forecast for business {business_id}"
        if product_ids:
            query_text += f" for products: {', '.join(product_ids)}"
        
        response = ai_service.process_query(
            user_id="system",
            business_id=business_id,
            query_text=query_text,
            assistant_type="GENERAL_QUERY"
        )
        
        response_time = int((time.time() - start_time) * 1000)
        
        return {
            "status": "completed",
            "business_id": business_id,
            "product_ids": product_ids or [],
            "forecast": response.get("response", ""),
            "response_time_ms": response_time,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        self.retry(countdown=60, exc=e)


@shared_task
def cleanup_old_ai_jobs(days_old: int = 30):
    from app.db.db import get_db, AIConversation
    from datetime import timedelta
    
    try:
        db = next(get_db())
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        deleted_count = db.query(AIConversation).filter(
            AIConversation.created_at < cutoff_date
        ).delete()
        
        db.commit()
        
        return {
            "status": "completed",
            "deleted_conversations": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
    
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
    finally:
        db.close()
