import requests
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
from app.core.config import settings


def hash_url(url:str) -> str:
    "Crea una huella digital para cada URL para evitar duplicados"
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def scrape_elpais_portada() -> List[Dict]:
    url = settings.SCRAPER_TARGET_URL

    try:
        response = requests.get(url)
        response.raise_for_status() # Lanza error si no es 200
        
        soup = BeautifulSoup(response.text, 'html.parser')
        noticias_limpias = []

        # En El País, las noticias suelen estar en etiquetas <article>
        articulos = soup.find_all('article')

        for articulo in articulos[:10]:
            # Buscamos el titular, que suele ser un h2
            h2 = articulo.find('h2')
            if h2 and h2.find('a'):
                etiqueta_link= h2.find('a')
                href =etiqueta_link['href']

                #Normalizamos la URL
                url_completa= f"https://elpais.com{href}" if href.startswith("/") else href

                noticias_limpias.append({
                    "url":url_completa,
                    "url_hash": hash_url(url_completa),
                    "titulo": etiqueta_link.text.strip(),
                    "fuente": "El País-portada",
                    "raw_content": str(articulo),
                    "scraped_at": datetime.now().isoformat()
                    
                })


        return noticias_limpias

    except Exception as e:
        print(f"Error en scrape_elpais_portada: {e}")
        return []
