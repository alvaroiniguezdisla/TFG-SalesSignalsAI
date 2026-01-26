# ----------------------------------------------------------------------------------
# TEST DE SCHEDULER (Planificador)
# Qué hace esto: Verifica que el sistema está programado para ejecutarse cada 6 horas.
# Para qué sirve: Para asegurar que el servidor "recuerda" ejecutar el trabajo solo y no se duerme.
# ----------------------------------------------------------------------------------

from unittest.mock import patch, MagicMock
from app.core.scheduler import start_scheduler, job_ejecutar_pipeline

def test_configuracion_scheduler():
    
    # Usamos 'patch' para no crear un scheduler real, sino un "doble" (mock)
    with patch("app.core.scheduler.BackgroundScheduler") as MockScheduler:
        # Instanciamos el mock
        mock_instance = MockScheduler.return_value
        
        # Ejecutamos la función que queremos probar
        start_scheduler()
        
        # VERIFICACIONES:
        
        # 1. ¿Se ha añadido el trabajo (job)?
        # Verificamos que add_job se llamó con nuestra función y el intervalo correcto (360 min = 6h)
        mock_instance.add_job.assert_called_with(
            job_ejecutar_pipeline, 
            "interval", 
            minutes=360
        )
        
        # 2. ¿Se ha iniciado el scheduler?
        mock_instance.start.assert_called_once()
        
        print("Test Scheduler: Configuración de intervalo (6h) correcta.")
