import requests
import os
from bs4 import BeautifulSoup
from typing import List, Dict
from dotenv import load_dotenv
from app.core.config import settings


# Cargar variables de entorno desde .env
load_dotenv()

def obtener_noticias() -> List[Dict[str, str]]:
    url = settings.SCRAPER_TARGET_URL
    try:
        response = requests.get(url)
        response.raise_for_status() # Lanza error si no es 200
        
        soup = BeautifulSoup(response.text, 'html.parser')
        noticias = []

        # En El País, las noticias suelen estar en etiquetas <article>
        articulos = soup.find_all('article')

        for articulo in articulos[:10]:
            # Buscamos el titular, que suele ser un h2
            titulo_tag = articulo.find('h2')
            if titulo_tag:
                link_tag = titulo_tag.find('a')
                if link_tag:
                    titulo = link_tag.text.strip()
                    link = link_tag['href']

                    # A veces los enlaces son relativos
                    if link.startswith('/'):
                        link = f'https://elpais.com{link}'

                    noticias.append({
                        'titulo': titulo,
                        'link': link
                    })
        return noticias
    except Exception as e:
        print(f"Error haciendo scraping: {e}")
        return []
