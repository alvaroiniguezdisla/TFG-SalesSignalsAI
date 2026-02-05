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
    1. Ejecuta el pipeline de ingesta (scrape, deduplicación, IA)
    2. Envía notificaciones por email a usuarios según sus preferencias
    """
    logger.info("[SCHEDULER] Iniciando ejecución programada del Pipeline...")

    try:
        # 1. Ejecutar pipeline de ingesta
        pipeline = NewsPipeline()
        pipeline.ejecutar()
        logger.info("[SCHEDULER] Pipeline de ingesta completado.")
        
        # 2. Enviar notificaciones por email
        from app.services.notificaciones.notificador import enviar_notificaciones_a_todos
        enviados = enviar_notificaciones_a_todos()
        logger.info(f"[SCHEDULER] Notificaciones enviadas: {enviados}")
        
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


