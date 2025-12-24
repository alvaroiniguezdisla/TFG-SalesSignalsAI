import logging
from typing import List,Dict, Any
#Importamos los metodos de extraccion de noticias
from app.services.extraccion.rss import obtener_noticias_rss
from app.services.extraccion.scraper import scrape_elpais_portada
from app.services.extraccion.browser import obtener_noticias_browser

# Configuramos un log para ver qué está pasando por debajo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsExtractorManager:
    """
    Clase en la que se va a encargar de obtenr noticias en el siguiente orden:
    1. RSS
    2. Scraper
    3. Browser
    """
    def obtener_noticias(self) -> List[Dict[str, Any]]:
        noticias=[]

        #1. Intento RSS
        try:
            logger.info("Intentando obtener noticias con RSS")
            noticias=obtener_noticias_rss()
            if noticias:
                logger.info(f" ÉXITO al obtener noticias con RSS. Se obtuvieron {len(noticias)} noticias con RSS")
                return noticias
            else:
                logger.warning("No se obtuvieron noticias con RSS")
                
        except Exception as e:
            logger.error(f"Error al obtener noticias con RSS: {e}")

        #2. Intento Scraper
        try:
            logger.info("Intentando obtener noticias con Scraper")
            noticias=scrape_elpais_portada()
            if noticias:
                logger.info(f" ÉXITO al obtener noticias con Scraper. Se obtuvieron {len(noticias)} noticias con Scraper")
                return noticias
            else:
                logger.warning("No se obtuvieron noticias con Scraper")
                
        except Exception as e:
            logger.error(f"Error al obtener noticias con Scraper: {e}")

        #3. Intento Browser
        try:
            logger.info("Intentando obtener noticias con Browser")
            noticias=obtener_noticias_browser()
            if noticias:
                logger.info(f" ÉXITO al obtener noticias con Browser. Se obtuvieron {len(noticias)} noticias con Browser")
                return noticias
            else:
                logger.warning("No se obtuvieron noticias con Browser")
                
        except Exception as e:
            logger.error(f"Error al obtener noticias con Browser: {e}")

        #4. Si no se obtuvieron noticias, devuelvo una lista vacía
        logger.error("TODOS LOS METODOS HAN FALLADO. No se obtuvieron noticias")
        return []

# Instacia global para usar en pipeline
extractor = NewsExtractorManager()