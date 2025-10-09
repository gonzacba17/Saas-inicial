"""
Notifications API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging
import os
from pathlib import Path

from app.db.db import get_db, User
from app.api.v1.auth import get_current_user
from app.schemas import (
    NotificationEvent,
    NotificationResponse,
    EmailTemplate,
    TestNotificationRequest,
    NotificationStatusResponse,
    NotificationEventType
)
from app.services_directory.notification_service import notification_service
from app.services_directory.email_service import email_service
from app.services_directory.push_service import push_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    event: NotificationEvent,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a notification to a user.
    """
    try:
        result = await notification_service.notify_event(
            event_type=event.event_type,
            payload=event.payload,
            user_email=event.user_email,
            user_id=event.user_id,
            user_name=event.user_name,
            channel=event.channel
        )
        
        return NotificationResponse(**result)
        
    except Exception as e:
        logger.error(f"Send notification error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send notification: {str(e)}"
        )


@router.post("/test", response_model=NotificationResponse)
async def test_notification(
    request: TestNotificationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send a test notification (for testing purposes).
    """
    try:
        test_payload = request.test_data or {
            "comprobante": {
                "id": "test-123",
                "tipo": "factura_a",
                "numero": "0001-00000001",
                "total": 1000.0,
                "fecha_emision": "2025-10-07T10:00:00"
            }
        }
        
        result = await notification_service.notify_event(
            event_type=request.notification_type,
            payload=test_payload,
            user_email=request.recipient_email,
            user_id=str(current_user.id),
            user_name=current_user.username,
            channel="email"
        )
        
        return NotificationResponse(**result)
        
    except Exception as e:
        logger.error(f"Test notification error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test notification: {str(e)}"
        )


@router.get("/templates", response_model=List[EmailTemplate])
def list_email_templates(
    current_user: User = Depends(get_current_user)
):
    """
    List available email templates.
    """
    try:
        templates_dir = Path(__file__).parent.parent.parent / "templates" / "emails"
        
        templates = [
            EmailTemplate(
                name="vencimiento_alert.html",
                subject="Alerta de Vencimiento",
                description="Notifica sobre un vencimiento próximo o vencido",
                variables=["user_name", "vencimiento", "dias_restantes"]
            ),
            EmailTemplate(
                name="comprobante_created.html",
                subject="Nuevo Comprobante Registrado",
                description="Notifica sobre un nuevo comprobante creado",
                variables=["user_name", "comprobante"]
            ),
            EmailTemplate(
                name="daily_summary.html",
                subject="Resumen Diario",
                description="Resumen diario de actividad",
                variables=["user_name", "summary_data"]
            ),
            EmailTemplate(
                name="chatbot_insight.html",
                subject="Insight del Chatbot",
                description="Notifica sobre un insight importante del chatbot",
                variables=["user_name", "insight", "context"]
            )
        ]
        
        return templates
        
    except Exception as e:
        logger.error(f"List templates error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list templates: {str(e)}"
        )


@router.get("/status", response_model=NotificationStatusResponse)
def notification_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get status of notification services.
    """
    try:
        templates_dir = Path(__file__).parent.parent.parent / "templates" / "emails"
        templates_count = len(list(templates_dir.glob("*.html"))) if templates_dir.exists() else 0
        
        celery_active = False
        try:
            from app.core.celery_app import celery_app
            inspector = celery_app.control.inspect()
            active_workers = inspector.active()
            celery_active = active_workers is not None and len(active_workers) > 0
        except:
            pass
        
        return NotificationStatusResponse(
            email_service_available=email_service.is_available(),
            push_service_available=push_service.is_available(),
            celery_worker_active=celery_active,
            templates_loaded=templates_count,
            message="Notification services operational" if email_service.is_available() else "Running in mock mode"
        )
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check status: {str(e)}"
        )


@router.post("/schedule/vencimiento-check")
def trigger_vencimiento_check(
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Manually trigger vencimiento check (admin only).
    """
    if not current_user.is_superuser and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can trigger scheduled tasks"
        )
    
    try:
        from app.tasks.scheduled_tasks import check_vencimientos_proximos
        
        task = check_vencimientos_proximos.delay()
        
        return {
            "success": True,
            "message": "Vencimiento check task scheduled",
            "task_id": task.id
        }
        
    except Exception as e:
        logger.error(f"Trigger vencimiento check error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger task: {str(e)}"
        )


@router.post("/schedule/daily-summary")
def trigger_daily_summary(
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger daily summary (admin only).
    """
    if not current_user.is_superuser and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can trigger scheduled tasks"
        )
    
    try:
        from app.tasks.scheduled_tasks import send_daily_summary
        
        task = send_daily_summary.delay()
        
        return {
            "success": True,
            "message": "Daily summary task scheduled",
            "task_id": task.id
        }
        
    except Exception as e:
        logger.error(f"Trigger daily summary error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger task: {str(e)}"
        )
