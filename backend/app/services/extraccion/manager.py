import logging
from typing import List,Dict, Any
from app.services.extraccion.rss import obtener_noticias_rss
from app.services.extraccion.scraper import scrape_noticias
from app.services.extraccion.browser import obtener_noticias_browser
from app.services.almacenamiento.database import get_supabase_service
from app.core.deduplication import es_titulo_similar, fusionar_datos_noticia

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsExtractorManager:
    """
    Gestor de estrategia de extracción en cascada (RSS -> HTML -> Browser).
    """
    def __init__(self):
        # Se rellena en cada ejecución de obtener_noticias()
        self._ultimas_fuentes_caidas: List[Dict[str, Any]] = []

    def get_ultimas_fuentes_caidas(self) -> List[Dict[str, Any]]:
        """Devuelve incidencias de fuentes detectadas en la última ingesta."""
        return self._ultimas_fuentes_caidas

    def obtener_noticias(self) -> List[Dict[str, Any]]:
        todas_las_noticias = []
        self._ultimas_fuentes_caidas = []
        
        # Leemos la configuración dinámicamente desde DB
        db = get_supabase_service()
        app_config = db.get_app_config()
        rss_sources = app_config.get("rss_sources", [])
        
        if not rss_sources:
            logger.warning("No hay fuentes RSS configuradas en la base de datos.")
            return []

        for source in rss_sources:
            nombre = source.get('name', 'Desconocido')
            logger.info(f"---Procesando Fuente: {nombre} ---")
            
            noticias_fuente = []
            exito = False
            errores_fuente = []
            
            rss_url = source.get('url') # La URL de RSS
            html_url = source.get('scraper_url') # La URL de respaldo para scraper y browser

            # 1. INTENTO RSS
            if rss_url:
                try:
                    logger.info(f"RSS: {rss_url}")
                    noticias_fuente = obtener_noticias_rss(rss_url, nombre)
                    if noticias_fuente:
                        logger.info(f"RSS OK: {len(noticias_fuente)} noticias")
                        exito = True
                    else:
                        msg = f"RSS sin noticias ({rss_url})"
                        errores_fuente.append(msg)
                        logger.warning(f"[FUENTE_CAIDA] {nombre}: {msg}")
                except Exception as e:
                    msg = f"RSS error ({rss_url}): {e}"
                    errores_fuente.append(msg)
                    logger.warning(f"[FUENTE_CAIDA] {nombre}: {msg}")

            # 2. INTENTO SCRAPER 
            if not exito and html_url:
                try:
                    logger.info(f"Scraper: {html_url}")
                    noticias_fuente = scrape_noticias(html_url, nombre)
                    if noticias_fuente:
                        logger.info(f"Scraper OK: {len(noticias_fuente)} noticias")
                        exito = True
                    else:
                        msg = f"Scraper sin noticias ({html_url})"
                        errores_fuente.append(msg)
                        logger.warning(f"[FUENTE_CAIDA] {nombre}: {msg}")
                except Exception as e:
                    msg = f"Scraper error ({html_url}): {e}"
                    errores_fuente.append(msg)
                    logger.warning(f"[FUENTE_CAIDA] {nombre}: {msg}")

            # 3. INTENTO BROWSER 
            if not exito and html_url:
                try:
                    logger.info(f"Browser: {html_url}")
                    noticias_fuente = obtener_noticias_browser(html_url, nombre)
                    if noticias_fuente:
                        logger.info(f"Browser OK: {len(noticias_fuente)} noticias")
                        exito = True
                    else:
                        msg = f"Browser sin noticias ({html_url})"
                        errores_fuente.append(msg)
                        logger.warning(f"[FUENTE_CAIDA] {nombre}: {msg}")
                except Exception as e:
                    msg = f"Browser error ({html_url}): {e}"
                    errores_fuente.append(msg)
                    logger.warning(f"[FUENTE_CAIDA] {nombre}: {msg}")

            # ACUMULAMOS resultados
            if noticias_fuente:
                todas_las_noticias.extend(noticias_fuente)
            else:
                logger.error(f"Imposible obtener noticias de {nombre} por ningún método.")
                self._ultimas_fuentes_caidas.append({
                    "fuente": nombre,
                    "errores": errores_fuente or ["Sin resultados por ningún método"],
                })

        if self._ultimas_fuentes_caidas:
            nombres = ", ".join(item["fuente"] for item in self._ultimas_fuentes_caidas)
            logger.warning(
                f"[FUENTES_CAIDAS] {len(self._ultimas_fuentes_caidas)} fuente(s) con incidencias: {nombres}"
            )

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

_extractor_manager_instance = None

def get_extractor_manager() -> NewsExtractorManager:
    global _extractor_manager_instance
    if _extractor_manager_instance is None:
        _extractor_manager_instance = NewsExtractorManager()
    return _extractor_manager_instance
