import feedparser 
from typing import List, Dict
from app.core.config import settings

def obtener_noticias_rss() -> List[Dict[str, str]]:
    # URL del feed RSS del config
    url_feed = settings.RSS_TARGET_URL
    #Parseamos el XML del feed
    feed = feedparser.parse(url_feed)
    noticias=[]

    # Recorremos las primeras 10 entradas
    for entry in feed.entries[:10]:
        noticias.append({
            "titulo": entry.title,
            "link" : entry.link,
            # El RSS a veces trae un resumen , lo aprovechamos si existe
            "resumen": entry.summary if 'summary' in entry else ""
        })

    return noticias