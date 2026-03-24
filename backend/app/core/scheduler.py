from apscheduler.schedulers.background import BackgroundScheduler
from app.services.orquestacion.pipeline import NewsPipeline
import logging
from app.services.notificaciones.notificador import enviar_notificaciones_a_todos

#Configuramos el logger
logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)

def job_ejecutar_pipeline():
    """
    Esta función se ejecutará automáticamente cada 6 horas.
    1. Ejecuta el pipeline de ingesta (scrape, deduplicación, IA)
    2. Envía notificaciones por Teams a usuarios según sus preferencias
    """
    logger.info("[SCHEDULER] Iniciando ejecución programada del Pipeline...")

    try:
        # 1. Ejecutar pipeline de ingesta
        pipeline = NewsPipeline()
        pipeline.ejecutar()
        logger.info("[SCHEDULER] Pipeline de ingesta completado.")
        
        # 2. Enviar notificaciones por Teams
        enviados = enviar_notificaciones_a_todos()
        logger.info(f"[SCHEDULER] Notificaciones enviadas: {enviados}")
        
        logger.info("[SCHEDULER] Ejecución finalizada correctamente.")
    
    except Exception as e:
        logger.error(f"[SCHEDULER] Error en la ejecución programada: {e}")
        

def start_scheduler():
    """
    Configura y arranca el planificador.
    """
    scheduler = BackgroundScheduler()

    # Configuramos cada cuanto tiempo se ejecuta 
    # Ejecutamos cada 6 horas (minutes=360)
    scheduler.add_job(job_ejecutar_pipeline, "interval", minutes=360)
    
    # Arrancamos el planificador
    scheduler.start()
    logger.info("[SCHEDULER] Planificador iniciado.")

if __name__ == "__main__":
    # Permite ejecutar el flujo completo a mano (Scraping + IA + Supabase + Teams)
    logging.basicConfig(level=logging.INFO)
    logger.info("Iniciando ejecución manual completa de SIMULADOR SCHEDULER...")
    job_ejecutar_pipeline()
    logger.info("Simulación terminada.")
