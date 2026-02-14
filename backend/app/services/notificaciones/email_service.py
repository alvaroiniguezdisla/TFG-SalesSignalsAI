"""
Servicio de envío de emails via Gmail SMTP.
Usado para notificar a usuarios sobre noticias relevantes.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.services.notificaciones.templates import generar_html_resumen

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_timeout = 30  # Timeout de 30 segundos
        self.sender_email = settings.GMAIL_USER
        self.password = settings.GMAIL_APP_PASSWORD

    def enviar_resumen(self, destinatario: str, nombre: str, noticias: list) -> bool:
        """
        Envía un email con el resumen de noticias personalizadas.
        
        Args:
            destinatario: Email del usuario
            nombre: Nombre del usuario para personalizar
            noticias: Lista de noticias filtradas para este usuario
        
        Returns:
            True si se envió correctamente, False en caso de error
        """
        if not noticias:
            return False

        if not self.sender_email or not self.password:
            logger.warning("Credenciales de Gmail no configuradas en .env")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"SalesSignals: {len(noticias)} nuevas señales para ti"
            msg["From"] = self.sender_email
            msg["To"] = destinatario

            # Generar contenido HTML
            html_content = generar_html_resumen(nombre, noticias)
            msg.attach(MIMEText(html_content, "html"))

            # Enviar con timeout
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.smtp_timeout) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, destinatario, msg.as_string())

            logger.info(f"Email enviado a {destinatario}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"Error SMTP enviando a {destinatario}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error enviando email a {destinatario}: {e}")
            return False


# Instancia global del servicio
email_service = EmailService()
