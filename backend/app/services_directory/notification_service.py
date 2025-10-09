"""
Centralized notification service that handles all notification events.
Dispatches to email and push services based on user preferences.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from app.services_directory.email_service import email_service
from app.services_directory.push_service import push_service

logger = logging.getLogger(__name__)


class NotificationEventType(str, Enum):
    """Supported notification event types."""
    COMPROBANTE_CREATED = "comprobante_created"
    VENCIMIENTO_PROXIMO = "vencimiento_proximo"
    VENCIMIENTO_VENCIDO = "vencimiento_vencido"
    CHATBOT_INSIGHT = "chatbot_insight"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_REPORT = "weekly_report"
    SYSTEM_ALERT = "system_alert"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    PUSH = "push"
    BOTH = "both"


class NotificationService:
    """Centralized service for managing all notifications."""
    
    def __init__(self):
        """Initialize notification service."""
        self.email_service = email_service
        self.push_service = push_service
        logger.info("Notification service initialized")
    
    async def notify_event(
        self,
        event_type: NotificationEventType,
        payload: Dict[str, Any],
        user_email: str,
        user_id: str,
        user_name: str,
        channel: NotificationChannel = NotificationChannel.BOTH
    ) -> Dict[str, Any]:
        """
        Main method to notify user about an event.
        
        Args:
            event_type: Type of event
            payload: Event data
            user_email: User's email
            user_id: User's ID
            user_name: User's name
            channel: Notification channel (email/push/both)
        
        Returns:
            Dict with notification results
        """
        results = {
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "email_sent": False,
            "push_sent": False,
            "email_result": None,
            "push_result": None
        }
        
        try:
            if channel in [NotificationChannel.EMAIL, NotificationChannel.BOTH]:
                email_result = await self._send_email_for_event(
                    event_type, payload, user_email, user_name
                )
                results["email_sent"] = email_result.get("success", False)
                results["email_result"] = email_result
            
            if channel in [NotificationChannel.PUSH, NotificationChannel.BOTH]:
                push_result = await self._send_push_for_event(
                    event_type, payload, user_id
                )
                results["push_sent"] = push_result.get("success", False)
                results["push_result"] = push_result
            
            results["success"] = results["email_sent"] or results["push_sent"]
            
            logger.info(f"Notification sent for {event_type} to user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error in notify_event: {e}")
            results["success"] = False
            results["error"] = str(e)
            return results
    
    async def _send_email_for_event(
        self,
        event_type: NotificationEventType,
        payload: Dict[str, Any],
        recipient: str,
        user_name: str
    ) -> Dict[str, Any]:
        """Send email notification based on event type."""
        if event_type == NotificationEventType.COMPROBANTE_CREATED:
            return await self.email_service.send_comprobante_notification(
                recipient=recipient,
                comprobante=payload.get("comprobante", {}),
                user_name=user_name
            )
        
        elif event_type in [NotificationEventType.VENCIMIENTO_PROXIMO, 
                           NotificationEventType.VENCIMIENTO_VENCIDO]:
            return await self.email_service.send_vencimiento_alert(
                recipient=recipient,
                vencimiento=payload.get("vencimiento", {}),
                user_name=user_name
            )
        
        elif event_type == NotificationEventType.CHATBOT_INSIGHT:
            return await self.email_service.send_chatbot_insight(
                recipient=recipient,
                user_name=user_name,
                insight=payload.get("insight", ""),
                context_data=payload.get("context", {})
            )
        
        elif event_type == NotificationEventType.DAILY_SUMMARY:
            return await self.email_service.send_daily_summary(
                recipient=recipient,
                user_name=user_name,
                summary_data=payload.get("summary", {})
            )
        
        else:
            return await self.email_service.send_email(
                recipient=recipient,
                subject=f"Notificación: {event_type}",
                body=str(payload)
            )
    
    async def _send_push_for_event(
        self,
        event_type: NotificationEventType,
        payload: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Send push notification based on event type."""
        if event_type == NotificationEventType.COMPROBANTE_CREATED:
            return await self.push_service.send_comprobante_notification(
                user_id=user_id,
                comprobante=payload.get("comprobante", {})
            )
        
        elif event_type in [NotificationEventType.VENCIMIENTO_PROXIMO,
                           NotificationEventType.VENCIMIENTO_VENCIDO]:
            return await self.push_service.send_vencimiento_alert(
                user_id=user_id,
                vencimiento=payload.get("vencimiento", {})
            )
        
        elif event_type == NotificationEventType.CHATBOT_INSIGHT:
            return await self.push_service.send_chatbot_insight(
                user_id=user_id,
                insight=payload.get("insight", "")
            )
        
        elif event_type == NotificationEventType.DAILY_SUMMARY:
            return await self.push_service.send_daily_summary(
                user_id=user_id,
                summary_data=payload.get("summary", {})
            )
        
        else:
            title = f"Notificación: {event_type}"
            message = str(payload)[:100]
            return await self.push_service.send_push(user_id, title, message)
    
    async def notify_comprobante_created(
        self,
        comprobante: Dict[str, Any],
        user_email: str,
        user_id: str,
        user_name: str,
        channel: NotificationChannel = NotificationChannel.BOTH
    ) -> Dict[str, Any]:
        """Notify when a new comprobante is created."""
        return await self.notify_event(
            event_type=NotificationEventType.COMPROBANTE_CREATED,
            payload={"comprobante": comprobante},
            user_email=user_email,
            user_id=user_id,
            user_name=user_name,
            channel=channel
        )
    
    async def notify_vencimiento_proximo(
        self,
        vencimiento: Dict[str, Any],
        user_email: str,
        user_id: str,
        user_name: str,
        dias_restantes: int,
        channel: NotificationChannel = NotificationChannel.BOTH
    ) -> Dict[str, Any]:
        """Notify when a vencimiento is coming up."""
        vencimiento_data = vencimiento.copy()
        vencimiento_data["dias_restantes"] = dias_restantes
        
        return await self.notify_event(
            event_type=NotificationEventType.VENCIMIENTO_PROXIMO,
            payload={"vencimiento": vencimiento_data},
            user_email=user_email,
            user_id=user_id,
            user_name=user_name,
            channel=channel
        )
    
    async def notify_vencimiento_vencido(
        self,
        vencimiento: Dict[str, Any],
        user_email: str,
        user_id: str,
        user_name: str,
        channel: NotificationChannel = NotificationChannel.BOTH
    ) -> Dict[str, Any]:
        """Notify when a vencimiento is overdue."""
        return await self.notify_event(
            event_type=NotificationEventType.VENCIMIENTO_VENCIDO,
            payload={"vencimiento": vencimiento},
            user_email=user_email,
            user_id=user_id,
            user_name=user_name,
            channel=channel
        )
    
    async def notify_chatbot_insight(
        self,
        insight: str,
        context: Dict[str, Any],
        user_email: str,
        user_id: str,
        user_name: str,
        channel: NotificationChannel = NotificationChannel.EMAIL
    ) -> Dict[str, Any]:
        """Notify when chatbot generates an important insight."""
        return await self.notify_event(
            event_type=NotificationEventType.CHATBOT_INSIGHT,
            payload={"insight": insight, "context": context},
            user_email=user_email,
            user_id=user_id,
            user_name=user_name,
            channel=channel
        )
    
    async def notify_daily_summary(
        self,
        summary_data: Dict[str, Any],
        user_email: str,
        user_id: str,
        user_name: str,
        channel: NotificationChannel = NotificationChannel.EMAIL
    ) -> Dict[str, Any]:
        """Send daily summary notification."""
        return await self.notify_event(
            event_type=NotificationEventType.DAILY_SUMMARY,
            payload={"summary": summary_data},
            user_email=user_email,
            user_id=user_id,
            user_name=user_name,
            channel=channel
        )
    
    async def notify_multiple_users(
        self,
        event_type: NotificationEventType,
        payload: Dict[str, Any],
        users: List[Dict[str, str]],
        channel: NotificationChannel = NotificationChannel.BOTH
    ) -> Dict[str, Any]:
        """
        Notify multiple users about an event.
        
        Args:
            event_type: Type of event
            payload: Event data
            users: List of dicts with user_id, user_email, user_name
            channel: Notification channel
        
        Returns:
            Dict with results for all users
        """
        results = []
        
        for user in users:
            result = await self.notify_event(
                event_type=event_type,
                payload=payload,
                user_email=user.get("user_email", ""),
                user_id=user.get("user_id", ""),
                user_name=user.get("user_name", ""),
                channel=channel
            )
            results.append(result)
        
        successful = sum(1 for r in results if r.get("success"))
        
        return {
            "success": successful > 0,
            "total_users": len(users),
            "successful": successful,
            "failed": len(users) - successful,
            "results": results
        }


notification_service = NotificationService()
