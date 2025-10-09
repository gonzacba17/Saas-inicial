"""
Email service for sending notifications using SMTP.
Supports HTML templates with Jinja2 and async sending.
"""
import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import asyncio

logger = logging.getLogger(__name__)

try:
    import aiosmtplib
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    logger.warning("Email dependencies not installed. Running in mock mode.")


class EmailService:
    """Service for sending emails with template support."""
    
    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.available = EMAIL_AVAILABLE
        
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", self.smtp_user)
        self.smtp_from_name = os.getenv("SMTP_FROM_NAME", "CaféBot IA")
        
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured. Email service will run in mock mode.")
            self.available = False
        
        if self.available:
            templates_dir = Path(__file__).parent.parent / "templates" / "emails"
            templates_dir.mkdir(parents=True, exist_ok=True)
            
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(templates_dir)),
                autoescape=select_autoescape(['html', 'xml'])
            )
            
            logger.info("Email service initialized successfully")
    
    def is_available(self) -> bool:
        """Check if email service is available."""
        return self.available
    
    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send email to recipient.
        
        Args:
            recipient: Email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            cc: Optional CC recipients
            bcc: Optional BCC recipients
        
        Returns:
            Dict with success status and message
        """
        if not self.available:
            return self._mock_send(recipient, subject, body)
        
        try:
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.smtp_from_name} <{self.smtp_from}>"
            message["To"] = recipient
            message["Subject"] = subject
            
            if cc:
                message["Cc"] = ", ".join(cc)
            if bcc:
                message["Bcc"] = ", ".join(bcc)
            
            part1 = MIMEText(body, "plain", "utf-8")
            message.attach(part1)
            
            if html_body:
                part2 = MIMEText(html_body, "html", "utf-8")
                message.attach(part2)
            
            recipients = [recipient]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )
            
            logger.info(f"Email sent successfully to {recipient}")
            
            return {
                "success": True,
                "recipient": recipient,
                "subject": subject,
                "message": "Email sent successfully",
                "mock": False
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {
                "success": False,
                "error": str(e),
                "recipient": recipient,
                "mock": False
            }
    
    async def send_template_email(
        self,
        recipient: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send email using Jinja2 template.
        
        Args:
            recipient: Email address
            subject: Email subject
            template_name: Template filename (e.g., 'vencimiento_alert.html')
            context: Template variables
            cc: Optional CC recipients
            bcc: Optional BCC recipients
        
        Returns:
            Dict with success status
        """
        if not self.available:
            return self._mock_send(recipient, subject, f"Template: {template_name}")
        
        try:
            template = self.jinja_env.get_template(template_name)
            
            html_body = template.render(**context)
            
            plain_body = self._html_to_plain(html_body)
            
            return await self.send_email(
                recipient=recipient,
                subject=subject,
                body=plain_body,
                html_body=html_body,
                cc=cc,
                bcc=bcc
            )
            
        except Exception as e:
            logger.error(f"Failed to send template email: {e}")
            return {
                "success": False,
                "error": str(e),
                "recipient": recipient,
                "template": template_name,
                "mock": False
            }
    
    async def send_vencimiento_alert(
        self,
        recipient: str,
        vencimiento: Dict[str, Any],
        user_name: str
    ) -> Dict[str, Any]:
        """Send vencimiento alert email."""
        context = {
            "user_name": user_name,
            "vencimiento": vencimiento,
            "tipo": vencimiento.get("tipo", ""),
            "descripcion": vencimiento.get("descripcion", ""),
            "monto": vencimiento.get("monto", 0),
            "fecha_vencimiento": vencimiento.get("fecha_vencimiento", ""),
            "dias_restantes": self._calculate_days_remaining(vencimiento.get("fecha_vencimiento"))
        }
        
        return await self.send_template_email(
            recipient=recipient,
            subject=f"⏰ Alerta de Vencimiento: {vencimiento.get('descripcion', 'Pago Pendiente')}",
            template_name="vencimiento_alert.html",
            context=context
        )
    
    async def send_comprobante_notification(
        self,
        recipient: str,
        comprobante: Dict[str, Any],
        user_name: str
    ) -> Dict[str, Any]:
        """Send comprobante created notification."""
        context = {
            "user_name": user_name,
            "comprobante": comprobante,
            "tipo": comprobante.get("tipo", ""),
            "numero": comprobante.get("numero", ""),
            "total": comprobante.get("total", 0),
            "fecha_emision": comprobante.get("fecha_emision", "")
        }
        
        return await self.send_template_email(
            recipient=recipient,
            subject=f"📄 Nuevo Comprobante: {comprobante.get('numero', 'N/A')}",
            template_name="comprobante_created.html",
            context=context
        )
    
    async def send_daily_summary(
        self,
        recipient: str,
        user_name: str,
        summary_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send daily summary email."""
        context = {
            "user_name": user_name,
            "date": summary_data.get("date", ""),
            "total_comprobantes": summary_data.get("total_comprobantes", 0),
            "total_monto": summary_data.get("total_monto", 0),
            "vencimientos_proximos": summary_data.get("vencimientos_proximos", []),
            "vencimientos_count": len(summary_data.get("vencimientos_proximos", []))
        }
        
        return await self.send_template_email(
            recipient=recipient,
            subject=f"📊 Resumen Diario - {summary_data.get('date', '')}",
            template_name="daily_summary.html",
            context=context
        )
    
    async def send_chatbot_insight(
        self,
        recipient: str,
        user_name: str,
        insight: str,
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send chatbot insight notification."""
        context = {
            "user_name": user_name,
            "insight": insight,
            "timestamp": context_data.get("timestamp", ""),
            "query": context_data.get("query", "")
        }
        
        return await self.send_template_email(
            recipient=recipient,
            subject="💡 CaféBot IA - Insight Importante",
            template_name="chatbot_insight.html",
            context=context
        )
    
    def _html_to_plain(self, html: str) -> str:
        """Convert HTML to plain text (basic implementation)."""
        import re
        text = re.sub('<[^<]+?>', '', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _calculate_days_remaining(self, fecha_vencimiento: Any) -> int:
        """Calculate days remaining until vencimiento."""
        try:
            from datetime import datetime
            if isinstance(fecha_vencimiento, str):
                fecha = datetime.fromisoformat(fecha_vencimiento.replace('Z', '+00:00'))
            else:
                fecha = fecha_vencimiento
            
            now = datetime.now()
            delta = fecha - now
            return max(0, delta.days)
        except:
            return 0
    
    def _mock_send(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """Mock email sending for development/testing."""
        logger.info(f"[MOCK EMAIL] To: {recipient} | Subject: {subject}")
        return {
            "success": False,
            "recipient": recipient,
            "subject": subject,
            "message": "Email service not configured. This is a mock response.",
            "mock": True
        }


email_service = EmailService()
