import app.services.inteligencia.llm_clasificacion_noticias
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.orquestacion.pipeline import NewsPipeline
import logging

#Configuramos el logger
logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

def job_ejecutar_pipeline():
    """
    Esta función se ejecutará automáticamente cada 6 horas.
    """
    logger.info("[SCHEDULER] Iniciando ejecución programada del Pipeline...")

    try:
        pipeline = NewsPipeline()
        pipeline.ejecutar()
        logger.info("[SCHEDULER] Ejecución finalizada correctamente.")
    
    except Exception as e:
        logger.error(f"[SCHEDULER] Error en la  ejecución programada: {e}")
        

def start_scheduler():
    """
    Configura y arranca el planificador.
    """
    scheduler= BackgroundScheduler()

    #Configuramos cada cuanto tiempo se ejecuta 
    #Ejecutamos cada 6 horas (minutes=360)
    scheduler.add_job(job_ejecutar_pipeline, "interval", minutes=360)
    
    #Arrancamos el planificador
    scheduler.start()
    logger.info("[SCHEDULER] Planificador iniciado.")


