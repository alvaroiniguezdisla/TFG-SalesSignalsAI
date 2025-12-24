import feedparser
import hashlib
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
from app.core.config import settings

def hash_url(url:str) -> str:
    return hashlib.md5(url.encode('utf-8')).hexdigest()

def obtener_noticias_rss() -> List[Dict[str, Any]]:
    url_feed = settings.RSS_TARGET_URL
    print(f"Leyendo RSS desde: {url_feed}")
    
    feed = feedparser.parse(url_feed)
    noticias=[]

    for entry in feed.entries[:10]:
        try:
            url_noticia = entry.link
            titulo = entry.title
            

            raw_content = ""
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
                response = requests.get(url_noticia, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    article_body = soup.find('article')
                    if article_body:
                        raw_content = str(article_body)
                    else:
                        raw_content = str(soup.body)
                else:
                    raw_content = entry.summary if 'summary' in entry else ""
            except Exception as e:
                print(f"Error enriqueciendo noticia {url_noticia}: {e}")
                raw_content = entry.summary if 'summary' in entry else ""

            noticias.append({
                "url": url_noticia,
                "url_hash": hash_url(url_noticia),
                "titulo": titulo,
                "fuente": "Cinco Dias (RSS+Hybrid)",
                "raw_content": raw_content,
                "resumen": entry.summary if 'summary' in entry else "",
                "scraped_at": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Error procesando entrada RSS: {e}")
            continue

    return noticias