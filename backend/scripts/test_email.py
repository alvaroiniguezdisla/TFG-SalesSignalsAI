"""
Script de prueba para verificar el envío de emails.
Ejecutar: python -m scripts.test_email
"""
from app.services.notificaciones.email_service import email_service
from app.core.config import settings

# Verificar configuración
print("Configuración Gmail:")
print(f"   GMAIL_USER: {settings.GMAIL_USER}")
print(f"   GMAIL_APP_PASSWORD: {'***configurado***' if settings.GMAIL_APP_PASSWORD else 'NO CONFIGURADO'}")

# Datos de prueba
noticias_test = [
    {
        "titulo": "Telefónica anuncia expansión de data centers en Madrid",
        "relevancia_ia": 85,
        "categoria_ia": "Expansión / Crecimiento",
        "categoria_producto_ia": "Servidores & Almacenamiento",
        "resumen_comercial_ia": "Telefónica ha anunciado una inversión de 500M€ en nuevos data centers. Oportunidad clara para equipamiento de servidores, almacenamiento y soluciones de refrigeración.",
        "url": "https://ejemplo.com/noticia-telefonica"
    },
    {
        "titulo": "Santander moderniza su infraestructura tecnológica",
        "relevancia_ia": 72,
        "categoria_ia": "Transformación Digital",
        "categoria_producto_ia": "Dispositivos Personales",
        "resumen_comercial_ia": "El banco invertirá en renovación de equipos para empleados. Potencial venta de portátiles, monitores y periféricos.",
        "url": "https://ejemplo.com/noticia-santander"
    }
]

# Enviar email de prueba
print("\nEnviando email de prueba...")
email_destino = settings.GMAIL_USER  # Se envía a sí mismo para probar

resultado = email_service.enviar_resumen(
    destinatario=email_destino,
    nombre="Test User",
    noticias=noticias_test
)

if resultado:
    print(f"\nEmail enviado correctamente a {email_destino}")
    print("   Revisa tu bandeja de entrada.")
else:
    print("\nError al enviar el email. Revisa la configuración.")
