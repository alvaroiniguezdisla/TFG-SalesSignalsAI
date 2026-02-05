"""
Script para probar el flujo completo de notificaciones.
Simula lo que hace el scheduler despues de una ingesta.
"""
import logging

# Configurar logging para ver los mensajes
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

from app.services.notificaciones.notificador import enviar_notificaciones_a_todos

print("=" * 50)
print("PRUEBA: Flujo completo de notificaciones")
print("=" * 50)

# Ejecutar el notificador
enviados = enviar_notificaciones_a_todos()

print("=" * 50)
print(f"RESULTADO: {enviados} emails enviados")
print("=" * 50)
