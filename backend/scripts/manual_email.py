# ----------------------------------------------------------------------------------
# SCRIPT MANUAL: Verificacion del envio de emails via Gmail
#
# Uso: python -m scripts.manual_email
#
# Que hace: Envia un email de prueba a la cuenta configurada en .env
# para verificar que las credenciales SMTP funcionan correctamente.
#
# Requisitos:
#   - GMAIL_USER y GMAIL_APP_PASSWORD configurados en .env
# ----------------------------------------------------------------------------------

from app.services.notificaciones.email_service import get_email_service
from app.core.config import settings


def ejecutar():
    print("Configuracion Gmail:")
    print(f"  GMAIL_USER: {settings.GMAIL_USER}")
    print(f"  GMAIL_APP_PASSWORD: {'***configurado***' if settings.GMAIL_APP_PASSWORD else 'NO CONFIGURADO'}")

    noticias_test = [
        {
            "titulo": "Telefonica anuncia expansion de data centers en Madrid",
            "relevancia_ia": 85,
            "categoria_ia": "Expansion / Crecimiento",
            "categoria_producto_ia": "Servidores & Almacenamiento",
            "resumen_comercial_ia": "Telefonica invertira 500M en nuevos data centers. "
                                    "Oportunidad para equipamiento de servidores y almacenamiento.",
            "url": "https://ejemplo.com/noticia-telefonica"
        },
        {
            "titulo": "Santander moderniza su infraestructura tecnologica",
            "relevancia_ia": 72,
            "categoria_ia": "Transformacion Digital",
            "categoria_producto_ia": "Dispositivos Personales",
            "resumen_comercial_ia": "El banco invertira en renovacion de equipos. "
                                    "Potencial venta de portatiles, monitores y perifericos.",
            "url": "https://ejemplo.com/noticia-santander"
        }
    ]

    email_destino = settings.GMAIL_USER
    print(f"\nEnviando email de prueba a {email_destino}...")

    email_service = get_email_service()
    resultado = email_service.enviar_resumen(
        destinatario=email_destino,
        nombre="Usuario de Prueba",
        noticias=noticias_test
    )

    if resultado:
        print("Email enviado correctamente. Revisa tu bandeja de entrada.")
    else:
        print("Error al enviar el email. Revisa la configuracion en .env.")


if __name__ == "__main__":
    ejecutar()
