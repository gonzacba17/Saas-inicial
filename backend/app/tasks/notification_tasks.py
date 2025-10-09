"""
Celery tasks for sending notifications.
"""
import asyncio
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.notification_tasks.send_notification_async")
def send_notification_async(
    event_type: str,
    payload: dict,
    user_email: str,
    user_id: str,
    user_name: str,
    channel: str = "both"
):
    """
    Celery task to send notification asynchronously.
    """
    try:
        from app.services_directory.notification_service import (
            notification_service,
            NotificationEventType,
            NotificationChannel
        )
        
        event_type_enum = NotificationEventType(event_type)
        channel_enum = NotificationChannel(channel)
        
        result = asyncio.run(
            notification_service.notify_event(
                event_type=event_type_enum,
                payload=payload,
                user_email=user_email,
                user_id=user_id,
                user_name=user_name,
                channel=channel_enum
            )
        )
        
        logger.info(f"Notification task completed: {event_type} for user {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Notification task failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task(name="app.tasks.notification_tasks.send_vencimiento_alert_task")
def send_vencimiento_alert_task(
    vencimiento: dict,
    user_email: str,
    user_id: str,
    user_name: str,
    dias_restantes: int
):
    """
    Celery task to send vencimiento alert.
    """
    try:
        from app.services_directory.notification_service import notification_service
        
        result = asyncio.run(
            notification_service.notify_vencimiento_proximo(
                vencimiento=vencimiento,
                user_email=user_email,
                user_id=user_id,
                user_name=user_name,
                dias_restantes=dias_restantes
            )
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Vencimiento alert task failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task(name="app.tasks.notification_tasks.send_comprobante_notification_task")
def send_comprobante_notification_task(
    comprobante: dict,
    user_email: str,
    user_id: str,
    user_name: str
):
    """
    Celery task to send comprobante notification.
    """
    try:
        from app.services_directory.notification_service import notification_service
        
        result = asyncio.run(
            notification_service.notify_comprobante_created(
                comprobante=comprobante,
                user_email=user_email,
                user_id=user_id,
                user_name=user_name
            )
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Comprobante notification task failed: {e}")
        return {"success": False, "error": str(e)}
