from playwright.sync_api import sync_playwright
from typing import List, Dict
import hashlib
from datetime import datetime
from app.core.config import settings 


def hash_url(url:str) -> str:
    return hashlib.md5(url.encode('utf-8')).hexdigest()

def obtener_noticias_browser() -> List[Dict[str, str]]:
    # "sync_playwright" es el gestor que arranca la maquinaria
    with sync_playwright() as p:
        # 1. Lanzamos un navegador Chromium
        # headless=True significa "sin cabeza" (invisible). 
        # Si ponemos  False, veremos el navegador abrirse en la pantalla
        browser = p.chromium.launch(headless=True)
        
        # 2. Abrimos una pestaña nueva
        page = browser.new_page()
        
        # 3. Vamos a la web
        page.goto(settings.SCRAPER_TARGET_URL)
        
        # 4. Esperamos a que existan los articulos (SOLO EN MAIN)
        page.wait_for_selector("main article")
        
        noticias = []
        # Seleccionamos todos los artículos DENTRO DE MAIN
        # Primero buscamos el main
        main_element = page.query_selector("main")
        if main_element:
            articulos = main_element.query_selector_all("article")
        else:
            articulos = page.query_selector_all("article")
        
        for articulo in articulos[:10]:
            # Buscamos el título (h2)
            titulo_element = articulo.query_selector("h2")
            if titulo_element:
                titulo = titulo_element.inner_text()
                
                # Buscamos el link
                link_element = titulo_element.query_selector("a")
                link = link_element.get_attribute("href") if link_element else ""
                
                # Arreglamos links relativos (Cinco Días)
                if link and link.startswith("/"):
                    link = f"https://cincodias.elpais.com{link}"
                
                url_completa = link
                
                noticias.append({
                    "url": url_completa,
                    "url_hash": hash_url(url_completa),
                    "titulo": titulo,
                    "fuente": "El País-Browser",
                    "raw_content": str(articulo.inner_html()), # Guardamos el HTML interno del articulo
                    "resumen": "Extraído con Navegador Real (Playwright)",
                    "scraped_at": datetime.now().isoformat()
                })
        
        # 5. Cerramos el navegador para liberar memoria
        browser.close()
        return noticias