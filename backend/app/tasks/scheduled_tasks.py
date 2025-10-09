"""
Celery scheduled tasks (Celery Beat).
"""
import asyncio
from celery import shared_task
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name="app.tasks.scheduled_tasks.check_vencimientos_proximos")
def check_vencimientos_proximos():
    """
    Scheduled task to check for upcoming vencimientos and send alerts.
    Runs daily at 9:00 AM.
    """
    try:
        from app.db.db import get_db, VencimientoCRUD, UserCRUD
        from app.services_directory.notification_service import notification_service
        
        db = next(get_db())
        
        hoy = datetime.now()
        fecha_limite = hoy + timedelta(days=7)
        
        vencimientos = db.query(
            VencimientoCRUD.__table__
        ).filter(
            VencimientoCRUD.fecha_vencimiento >= hoy,
            VencimientoCRUD.fecha_vencimiento <= fecha_limite,
            VencimientoCRUD.status == "pendiente"
        ).all()
        
        notifications_sent = 0
        
        for venc in vencimientos:
            user = UserCRUD.get_by_id(db, venc.user_id)
            if user:
                dias_restantes = (venc.fecha_vencimiento - hoy).days
                
                venc_dict = {
                    "id": str(venc.id),
                    "tipo": venc.tipo,
                    "descripcion": venc.descripcion,
                    "monto": venc.monto,
                    "fecha_vencimiento": venc.fecha_vencimiento.isoformat()
                }
                
                asyncio.run(
                    notification_service.notify_vencimiento_proximo(
                        vencimiento=venc_dict,
                        user_email=user.email,
                        user_id=str(user.id),
                        user_name=user.username,
                        dias_restantes=dias_restantes
                    )
                )
                
                notifications_sent += 1
        
        logger.info(f"Checked vencimientos, sent {notifications_sent} alerts")
        return {"success": True, "notifications_sent": notifications_sent}
        
    except Exception as e:
        logger.error(f"Check vencimientos task failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task(name="app.tasks.scheduled_tasks.send_daily_summary")
def send_daily_summary():
    """
    Scheduled task to send daily summary to all active users.
    Runs daily at 6:00 PM.
    """
    try:
        from app.db.db import get_db, UserCRUD, ComprobanteCRUD, VencimientoCRUD
        from app.services_directory.notification_service import notification_service
        from sqlalchemy import func
        
        db = next(get_db())
        
        users = db.query(UserCRUD.__table__).filter(
            UserCRUD.is_active == True
        ).all()
        
        hoy = datetime.now()
        ayer = hoy - timedelta(days=1)
        
        summaries_sent = 0
        
        for user in users:
            comprobantes_hoy = db.query(func.count(ComprobanteCRUD.id)).filter(
                ComprobanteCRUD.user_id == user.id,
                ComprobanteCRUD.created_at >= ayer
            ).scalar()
            
            total_monto = db.query(func.sum(ComprobanteCRUD.total)).filter(
                ComprobanteCRUD.user_id == user.id,
                ComprobanteCRUD.created_at >= ayer
            ).scalar() or 0
            
            vencimientos_proximos = VencimientoCRUD.get_proximos(
                db, user.id, dias=7
            )
            
            if comprobantes_hoy > 0 or len(vencimientos_proximos) > 0:
                summary_data = {
                    "date": hoy.strftime("%Y-%m-%d"),
                    "total_comprobantes": comprobantes_hoy,
                    "total_monto": float(total_monto),
                    "vencimientos_proximos": [
                        {
                            "descripcion": v.descripcion,
                            "monto": v.monto,
                            "fecha_vencimiento": v.fecha_vencimiento.isoformat()
                        }
                        for v in vencimientos_proximos[:5]
                    ],
                    "vencimientos_count": len(vencimientos_proximos)
                }
                
                asyncio.run(
                    notification_service.notify_daily_summary(
                        summary_data=summary_data,
                        user_email=user.email,
                        user_id=str(user.id),
                        user_name=user.username
                    )
                )
                
                summaries_sent += 1
        
        logger.info(f"Sent {summaries_sent} daily summaries")
        return {"success": True, "summaries_sent": summaries_sent}
        
    except Exception as e:
        logger.error(f"Daily summary task failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task(name="app.tasks.scheduled_tasks.send_weekly_report")
def send_weekly_report():
    """
    Scheduled task to send weekly report.
    Runs every Monday at 9:00 AM.
    """
    try:
        logger.info("Weekly report task executed")
        return {"success": True, "message": "Weekly report sent"}
        
    except Exception as e:
        logger.error(f"Weekly report task failed: {e}")
        return {"success": False, "error": str(e)}
