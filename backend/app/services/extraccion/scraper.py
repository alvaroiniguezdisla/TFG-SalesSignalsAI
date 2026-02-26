import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any
import logging
from app.core.utils import hash_url

logger = logging.getLogger(__name__)


def scrape_noticias(target_url: str,nombre_fuente: str="Scraper Genérico") -> List[Dict[str, Any]]:
    logger.info(f"[EXTRACCION_SCRAPER] Iniciando volcado HTML de {target_url} ({nombre_fuente})")
    try:
        # Añadimos cabeceras para parecer un navegador real y evitar el error 403
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Referer': 'https://www.google.com/'
        }
        response = requests.get(target_url, headers=headers, timeout=10)
        response.raise_for_status() # Lanza error si no es 200
        
        soup = BeautifulSoup(response.text, 'html.parser')
        noticias_limpias = []

        # BUSCAMOS SOLO EN <main> PARA EVITAR EL "TICKER" DE POLITICA DEL HEADER
        contenedor = soup.find('main')
        if not contenedor: 
            contenedor = soup # Fallback por si acaso

        # El Economista no usa <article> semántico, usa divs con clases específicas
        articulos = contenedor.find_all(['article', 'div'], class_=['articleContent', 'articleHeadline'])
        
        # SI NO HAY ARTICULOS 
        if not articulos:
            # Estrategia alternativa: Buscar h2 dentro del main y tratar su padre como artículo
            titulares = contenedor.find_all(['h2', 'h3'])
            # Filtramos solo los que tienen enlace
            articulos = [t.parent for t in titulares if t.find('a')]

        for item in articulos[:10]: # Aumentamos un poco por si acaso
            # Si es un <article>, buscamos h2. Si es un div padre, el h2/h3 ya está ahí
            h2 = item.find(['h2', 'h3'])
            if h2 and h2.find('a'):
                etiqueta_link= h2.find('a')
                href =etiqueta_link['href']

                #Normalizamos la URL de forma genérica
                url_completa= href
                if href.startswith("/"):
                    # Reconstruimos dominio base: protocol://domain.com
                    domain = "/".join(target_url.split("/")[:3])
                    url_completa= f"{domain}{href}"

                noticias_limpias.append({
                    "url":url_completa,
                    "url_hash": hash_url(url_completa),
                    "titulo": etiqueta_link.text.strip(),
                    "fuente": nombre_fuente,
                    "raw_content": str(item),
                    "resumen": "",
                    "published_at": None,
                    "scraped_at": datetime.now().isoformat()
                })


        return noticias_limpias

    except Exception as e:
        logger.error(f"[EXTRACCION_SCRAPER] Error procesando el HTML de {target_url}: {e}")
        return []
