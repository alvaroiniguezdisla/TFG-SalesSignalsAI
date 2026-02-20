# ----------------------------------------------------------------------------------
# TEST DEL PLANIFICADOR (SCHEDULER)
#
# Objetivo: Verificar que el planificador de tareas esta configurado correctamente
# y que la funcion que ejecuta cada 6 horas funciona como se espera.
#
# Que comprueba:
#   1. Que se registra la tarea con el intervalo de 360 minutos (6 horas).
#   2. Que el planificador se inicia correctamente.
#   3. Que la tarea programada ejecuta el pipeline y las notificaciones.
#   4. Que si el pipeline falla, el error se captura sin romper el scheduler.
# ----------------------------------------------------------------------------------

from unittest.mock import patch 
from app.core.scheduler import start_scheduler, job_ejecutar_pipeline


# --- Tests de start_scheduler (la configuracion) ---

def test_configuracion_intervalo():
    """
    Verifica que el planificador se configura con un intervalo de 360 minutos
    (6 horas) y que se inicia correctamente al arrancar la aplicacion.
    """
    with patch("app.core.scheduler.BackgroundScheduler") as MockScheduler:
        mock_instance = MockScheduler.return_value

        start_scheduler()

        mock_instance.add_job.assert_called_with(
            job_ejecutar_pipeline,
            "interval",
            minutes=360
        )
        mock_instance.start.assert_called_once()


# --- Tests de job_ejecutar_pipeline (la tarea que se ejecuta cada 6h) ---

@patch("app.core.scheduler.enviar_notificaciones_a_todos")
@patch("app.core.scheduler.NewsPipeline")
def test_job_ejecuta_pipeline_y_notificaciones(MockPipeline, MockNotificador):
    """
    Verifica que la tarea programada ejecuta los 2 pasos en orden:
    primero el pipeline de ingesta, luego el envio de notificaciones.
    """
    MockNotificador.return_value = 3  # Simula que se enviaron 3 emails

    job_ejecutar_pipeline()

    # Se creo y ejecuto el pipeline
    MockPipeline.return_value.ejecutar.assert_called_once()

    # Se enviaron las notificaciones
    MockNotificador.assert_called_once()


@patch("app.core.scheduler.enviar_notificaciones_a_todos")
@patch("app.core.scheduler.NewsPipeline")
def test_job_captura_error_sin_romper(MockPipeline, MockNotificador):
    """
    Si el pipeline falla (p.ej. Supabase caido), el scheduler no debe
    romperse. El error se logea y el scheduler sigue vivo para
    intentar de nuevo en 6 horas.
    """
    MockPipeline.return_value.ejecutar.side_effect = Exception("Supabase no responde")

    # No debe lanzar excepcion
    job_ejecutar_pipeline()

    # El pipeline se intento ejecutar
    MockPipeline.return_value.ejecutar.assert_called_once()

    # Las notificaciones NO se ejecutaron (porque el pipeline fallo antes)
    MockNotificador.assert_not_called()
