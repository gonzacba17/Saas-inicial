from typing import Optional, Dict, Any
from datetime import datetime
import time
from app.db.db import get_db, AIAuditLogCRUD


def log_ai_inference(
    user_id: Optional[str] = None,
    business_id: Optional[str] = None,
    model_name: str = "gpt-3.5-turbo",
    prompt: str = "",
    response: str = "",
    tokens_used: int = 0,
    response_time_ms: int = 0,
    endpoint: Optional[str] = None,
    status: str = "success",
    error_message: Optional[str] = None
) -> Dict[str, Any]:
    try:
        db = next(get_db())
        
        log_data = {
            "user_id": user_id,
            "business_id": business_id,
            "model_name": model_name,
            "prompt": prompt[:5000],
            "response": response[:10000],
            "tokens_used": tokens_used,
            "response_time_ms": response_time_ms,
            "endpoint": endpoint,
            "status": status,
            "error_message": error_message
        }
        
        audit_log = AIAuditLogCRUD.create(db, log_data)
        
        return {
            "log_id": str(audit_log.id),
            "timestamp": audit_log.timestamp.isoformat()
        }
    
    except Exception as e:
        return {
            "error": f"Failed to log AI inference: {str(e)}"
        }
    finally:
        db.close()


class AIAuditContext:
    def __init__(
        self,
        user_id: Optional[str] = None,
        business_id: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        endpoint: Optional[str] = None
    ):
        self.user_id = user_id
        self.business_id = business_id
        self.model_name = model_name
        self.endpoint = endpoint
        self.start_time = None
        self.prompt = ""
        self.response = ""
        self.tokens_used = 0
        self.status = "success"
        self.error_message = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        response_time_ms = int((time.time() - self.start_time) * 1000)
        
        if exc_type is not None:
            self.status = "error"
            self.error_message = str(exc_val)
        
        log_ai_inference(
            user_id=self.user_id,
            business_id=self.business_id,
            model_name=self.model_name,
            prompt=self.prompt,
            response=self.response,
            tokens_used=self.tokens_used,
            response_time_ms=response_time_ms,
            endpoint=self.endpoint,
            status=self.status,
            error_message=self.error_message
        )
        
        return False
