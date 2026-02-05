"""
Servicio de envío de emails via Gmail SMTP.
Usado para notificar a usuarios sobre noticias relevantes.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

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
            html_content = self._generar_html(nombre, noticias)
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

    def _generar_html(self, nombre: str, noticias: list) -> str:
        """Genera el HTML del email con las noticias."""
        noticias_html = ""
        for n in noticias[:10]:  # Máximo 10 noticias
            relevancia = n.get("relevancia_ia", 0)
            if relevancia >= 70:
                prioridad = "Alta"
                color = "#ef4444"
            elif relevancia >= 40:
                prioridad = "Media"
                color = "#f59e0b"
            else:
                prioridad = "Baja"
                color = "#22c55e"
            
            titulo = n.get('titulo', 'Sin título')
            categoria = n.get('categoria_ia', 'N/A')
            resumen = n.get('resumen_comercial_ia', '')[:200]
            url = n.get('url', '#')
            
            noticias_html += f"""
            <div style="border-left: 4px solid {color}; padding: 12px 16px; margin: 12px 0; background: #f8fafc; border-radius: 0 8px 8px 0;">
                <strong style="font-size: 16px; color: #1e293b;">{titulo}</strong><br>
                <small style="color: #64748b;">Prioridad: {prioridad} | Categoría: {categoria}</small><br>
                <p style="color: #475569; margin: 8px 0;">{resumen}...</p>
                <a href="{url}" style="color: #3b82f6; text-decoration: none; font-weight: 600;">Leer más →</a>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #ffffff;">
            <div style="text-align: center; margin-bottom: 24px;">
                <h1 style="color: #1e293b; margin: 0;">SalesSignalsAI</h1>
                <p style="color: #64748b; margin: 8px 0 0 0;">Tu asistente de señales comerciales</p>
            </div>
            
            <div style="background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; padding: 20px; border-radius: 12px; margin-bottom: 24px;">
                <h2 style="margin: 0 0 8px 0;">Hola {nombre}!</h2>
                <p style="margin: 0; opacity: 0.9;">Tienes <strong>{len(noticias)} nuevas señales</strong> basadas en tus preferencias.</p>
            </div>
            
            <h3 style="color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">Tus Señales Personalizadas</h3>
            
            {noticias_html}
            
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">
            
            <p style="color: #94a3b8; font-size: 12px; text-align: center;">
                Este email fue generado automáticamente por SalesSignalsAI.<br>
                Puedes actualizar tus preferencias en tu perfil de la aplicación.
            </p>
        </body>
        </html>
        """


# Instancia global del servicio
email_service = EmailService()
