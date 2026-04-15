# ----------------------------------------------------------------------------------
# SCRIPT MANUAL: Ejecucion del flujo de notificaciones
#
# Uso: python -m scripts.manual_notificador
#
# Que hace: Lanza el proceso de notificaciones completo, que:
#   1. Busca noticias recientes (ultimas 6h) con relevancia >= 40.
#   2. Obtiene los usuarios registrados y sus preferencias.
#   3. Filtra noticias por preferencias de cada usuario.
#   4. Envia notificaciones a Teams al usuario objetivo configurado.
#
# Requisitos:
#   - Credenciales Supabase configuradas en .env
#   - Credenciales de Microsoft Graph si se quiere probar el envio real a Teams
#   - Noticias recientes en la base de datos
# ----------------------------------------------------------------------------------

import logging

from app.services.notificaciones.notificador import enviar_notificaciones_a_todos

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")


def ejecutar():
    print("=" * 50)
    print("Ejecutando flujo completo de notificaciones")
    print("=" * 50)

    enviados = enviar_notificaciones_a_todos()

    print("=" * 50)
    print(f"Resultado: {enviados} notificaciones enviadas")
    print("=" * 50)


if __name__ == "__main__":
    ejecutar()
