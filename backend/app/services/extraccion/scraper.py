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

        # Buscamos de forma genérica contenedores semánticos de tipo artículo
        articulos = contenedor.find_all('article')
        
        # SI NO HAY ARTICULOS SEMÁNTICOS (Estrategia Fallback interna)
        if not articulos:
            # Estrategia alternativa: Buscar encabezados dentro del main y tratar a su contenedor padre como el artículo general
            titulares = contenedor.find_all(['h2', 'h3'])
            # Filtramos solo los encabezados que contengan un enlace (<a>) para evitar coger subtítulos basura
            articulos = [t.parent for t in titulares if t.find('a')]

        for item in articulos[:15]: 
            # 1. Búsqueda del nodo de título 
            titulo_nodo = item.find(['h2', 'h3'])
            
            if titulo_nodo and titulo_nodo.find('a'):
                etiqueta_link = titulo_nodo.find('a')
            else:
                # Estrategia de Fallback: Extracción del primer enlace disponible en el contenedor
                etiqueta_link = item.find('a')

            # Validación del elemento: Confirmación de hipervínculo y longitud mínima del texto para descartar iconos o imágenes
            if etiqueta_link and etiqueta_link.get('href') and len(etiqueta_link.text.strip()) > 5:
                href = etiqueta_link['href']

                #Normalizamos la URL de forma genérica (por si son rutas relativas)
                url_completa= href
                if href.startswith("/"):
                    domain = "/".join(target_url.split("/")[:3])
                    url_completa= f"{domain}{href}"

                # Intento de extraer resumen buscando la primera etiqueta de párrafo (<p>)
                p_tag = item.find('p')
                resumen_html = p_tag.text.strip() if p_tag else ""

                noticias_limpias.append({
                    "url": url_completa,
                    "url_hash": hash_url(url_completa),
                    "titulo": etiqueta_link.text.strip(),
                    "fuente": nombre_fuente,
                    "resumen": resumen_html,
                    "published_at": None,
                    "scraped_at": datetime.now().isoformat()
                })

        return noticias_limpias

    except Exception as e:
        logger.error(f"[EXTRACCION_SCRAPER] Error procesando el HTML de {target_url}: {e}")
        return []
