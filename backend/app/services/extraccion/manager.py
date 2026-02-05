import logging
from typing import List,Dict, Any
from app.services.extraccion.rss import obtener_noticias_rss
from app.services.extraccion.scraper import scrape_noticias
from app.services.extraccion.browser import obtener_noticias_browser
from app.core.config import settings
from app.core.deduplication import es_titulo_similar, fusionar_datos_noticia

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsExtractorManager:
    """
    Gestor de estrategia de extracción en cascada (RSS -> HTML -> Browser).
    """
    def obtener_noticias(self) -> List[Dict[str, Any]]:
        todas_las_noticias = []

        for source in settings.RSS_SOURCES:
            nombre = source['name']
            logger.info(f"---Procesando Fuente: {nombre} ---")
            
            noticias_fuente = []
            exito = False
            
            rss_url = source.get('url')
            html_url = source.get('scraper_url') # La URL de respaldo

            # 1. INTENTO RSS
            if rss_url:
                try:
                    logger.info(f"    RSS: {rss_url}")
                    noticias_fuente = obtener_noticias_rss(rss_url, nombre)
                    if noticias_fuente:
                        logger.info(f"    RSS OK: {len(noticias_fuente)} noticias")
                        exito = True
                except Exception as e:
                    logger.warning(f"    Falló RSS: {e}")

            # 2. INTENTO SCRAPER 
            if not exito and html_url:
                try:
                    logger.info(f"    Scraper: {html_url}")
                    noticias_fuente = scrape_noticias(html_url, nombre)
                    if noticias_fuente:
                        logger.info(f"    Scraper OK: {len(noticias_fuente)} noticias")
                        exito = True
                except Exception as e:
                    logger.warning(f"    Falló Scraper: {e}")

            # 3. INTENTO BROWSER 
            if not exito and html_url:
                try:
                    logger.info(f"    Browser: {html_url}")
                    noticias_fuente = obtener_noticias_browser(html_url, nombre)
                    if noticias_fuente:
                        logger.info(f"    Browser OK: {len(noticias_fuente)} noticias")
                        exito = True
                except Exception as e:
                    logger.error(f"    Falló todo para {nombre}")

            # ACUMULAMOS resultados
            if noticias_fuente:
                todas_las_noticias.extend(noticias_fuente)
            else:
                logger.error(f" Imposible obtener noticias de {nombre} por ningún método.")

        # 4. Deduplicación Semántica
        logger.info(f"Total noticias crudas: {len(todas_las_noticias)}")
        noticias_unicas = self.deduplicar_por_titulo(todas_las_noticias)
        logger.info(f"Total tras deduplicación: {len(noticias_unicas)}")

        return noticias_unicas
    
    def deduplicar_por_titulo(self, lista_noticias: List[Dict])-> List[Dict]:
        """
        Refactorizado para usar app.core.deduplication (lógica compartida).
        """
        unicas = []
        for nueva in lista_noticias:
            es_duplicada = False
            for existente in unicas:
                # Usamos la función compartida
                if es_titulo_similar(nueva['titulo'], existente['titulo']):
                    es_duplicada = True
                    
                    # Usamos la función de fusión compartida
                    cambios = fusionar_datos_noticia(existente, nueva)
                    if cambios:
                        logger.info(f"FUSIÓN: {existente['titulo']} <-- {nueva['titulo']}")
                    break 
            
            if not es_duplicada:
                unicas.append(nueva)
        
        return unicas

# Instacia global para usar en pipeline
extractor = NewsExtractorManager()