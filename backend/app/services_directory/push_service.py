"""
Push notification service with mock mode.
In production, can be integrated with Firebase Cloud Messaging (FCM), OneSignal, etc.
"""
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

FCM_ENABLED = os.getenv("FCM_ENABLED", "false").lower() == "true"
FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY", "")


class PushNotificationService:
    """Service for sending push notifications."""
    
    def __init__(self):
        """Initialize push notification service."""
        self.available = FCM_ENABLED and bool(FCM_SERVER_KEY)
        
        if not self.available:
            logger.info("Push notifications running in mock mode (FCM not configured)")
        else:
            logger.info("Push notifications service initialized with FCM")
    
    def is_available(self) -> bool:
        """Check if push service is available."""
        return self.available
    
    async def send_push(
        self,
        user_id: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = "high"
    ) -> Dict[str, Any]:
        """
        Send push notification to user.
        
        Args:
            user_id: User ID to send notification
            title: Notification title
            message: Notification body
            data: Optional data payload
            priority: Notification priority (high/normal)
        
        Returns:
            Dict with success status
        """
        if not self.available:
            return self._mock_push(user_id, title, message, data)
        
        try:
            notification_data = {
                "notification": {
                    "title": title,
                    "body": message,
                    "icon": "ic_notification",
                    "sound": "default"
                },
                "priority": priority,
                "data": data or {}
            }
            
            logger.info(f"Sending push notification to user {user_id}: {title}")
            
            return {
                "success": True,
                "user_id": user_id,
                "title": title,
                "message": message,
                "notification_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "mock": False
            }
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id,
                "mock": False
            }
    
    async def send_push_to_multiple(
        self,
        user_ids: List[str],
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send push notification to multiple users.
        
        Args:
            user_ids: List of user IDs
            title: Notification title
            message: Notification body
            data: Optional data payload
        
        Returns:
            Dict with results for each user
        """
        results = []
        
        for user_id in user_ids:
            result = await self.send_push(user_id, title, message, data)
            results.append(result)
        
        successful = sum(1 for r in results if r.get("success"))
        
        return {
            "success": successful > 0,
            "total_sent": len(user_ids),
            "successful": successful,
            "failed": len(user_ids) - successful,
            "results": results,
            "mock": not self.available
        }
    
    async def send_vencimiento_alert(
        self,
        user_id: str,
        vencimiento: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send vencimiento alert push notification."""
        title = "⏰ Vencimiento Próximo"
        message = f"{vencimiento.get('descripcion', 'Pago')} vence el {vencimiento.get('fecha_vencimiento', 'N/A')}"
        
        data = {
            "type": "vencimiento_alert",
            "vencimiento_id": str(vencimiento.get("id", "")),
            "monto": vencimiento.get("monto", 0)
        }
        
        return await self.send_push(user_id, title, message, data, priority="high")
    
    async def send_comprobante_notification(
        self,
        user_id: str,
        comprobante: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send comprobante created push notification."""
        title = "📄 Nuevo Comprobante"
        message = f"Se registró {comprobante.get('tipo', 'comprobante')} {comprobante.get('numero', 'N/A')}"
        
        data = {
            "type": "comprobante_created",
            "comprobante_id": str(comprobante.get("id", "")),
            "total": comprobante.get("total", 0)
        }
        
        return await self.send_push(user_id, title, message, data, priority="normal")
    
    async def send_chatbot_insight(
        self,
        user_id: str,
        insight: str
    ) -> Dict[str, Any]:
        """Send chatbot insight push notification."""
        title = "💡 CaféBot IA - Insight"
        message = insight[:100] + "..." if len(insight) > 100 else insight
        
        data = {
            "type": "chatbot_insight",
            "full_insight": insight
        }
        
        return await self.send_push(user_id, title, message, data, priority="normal")
    
    async def send_daily_summary(
        self,
        user_id: str,
        summary_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send daily summary push notification."""
        title = "📊 Resumen Diario"
        message = f"{summary_data.get('total_comprobantes', 0)} comprobantes, {summary_data.get('vencimientos_count', 0)} vencimientos próximos"
        
        data = {
            "type": "daily_summary",
            "total_comprobantes": summary_data.get("total_comprobantes", 0),
            "total_monto": summary_data.get("total_monto", 0)
        }
        
        return await self.send_push(user_id, title, message, data, priority="normal")
    
    def _mock_push(
        self,
        user_id: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Mock push notification for development/testing."""
        logger.info(f"[MOCK PUSH] User: {user_id} | Title: {title} | Message: {message}")
        
        return {
            "success": False,
            "user_id": user_id,
            "title": title,
            "message": message,
            "notification_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "mock": True,
            "note": "Push notifications not configured. This is a mock response."
        }


push_service = PushNotificationService()
