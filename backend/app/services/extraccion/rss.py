import feedparser
import requests
from typing import List, Dict, Any
from datetime import datetime
import logging
from app.core.utils import hash_url

logger = logging.getLogger(__name__)

def obtener_noticias_rss(url_feed: str, nombre_fuente: str="RSS Genérico") -> List[Dict[str, Any]]:
    logger.info(f"[EXTRACCION_RSS] Evaluando feed RSS: {url_feed} ({nombre_fuente})")
    
    # Fakeamos ser un navegador real para que el servidor no bloquee a feedparser
    headers_feed = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Referer': 'https://www.google.com/'
    }
    
    try:
        response_feed = requests.get(url_feed, headers=headers_feed, timeout=10)
        response_feed.raise_for_status() # Verifica si hubo error HTTP (ej: 404, 503)
        
        # Pasamos el XML a feedparser
        feed = feedparser.parse(response_feed.text)
    except Exception as e:
        logger.error(f"[EXTRACCION_RSS] Error critico descargando el feed {url_feed}: {e}")
        return []

    #Si el feed falla o está vacío
    if not feed.entries:
        logger.warning(f"[EXTRACCION_RSS] No se encontraron entradas validas en el feed de {nombre_fuente}")
        return []

    noticias = [] 
    for entry in feed.entries[:10]:
        try:
            url_noticia = entry.link
            titulo = entry.title
            resumen_texto = entry.summary if 'summary' in entry else ""

            noticias.append({
                "url": url_noticia,
                "url_hash": hash_url(url_noticia),
                "titulo": titulo,
                "fuente": nombre_fuente,
                "resumen": resumen_texto,
                "published_at": entry.get('published') or None,
                "scraped_at": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"[EXTRACCION_RSS] Error iterando sobre entrada RSS de {nombre_fuente}: {e}")
            continue

    return noticias