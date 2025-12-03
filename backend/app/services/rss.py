import feedparser 
from typing import List, Dict

def obtener_noticias_rss(url_feed: str = "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada") -> List[Dict[str, str]]:
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