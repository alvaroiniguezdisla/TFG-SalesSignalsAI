from playwright.sync_api import sync_playwright
from typing import List, Dict
from app.core.config import settings 

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
        
        # 4. Esperamos a que existan los articulos
        # Esto es lo que BeautifulSoup no puede hacer (esperar a JS).
        page.wait_for_selector("article")
        
        noticias = []
        # Seleccionamos todos los artículos (igual que hacíamos antes)
        articulos = page.query_selector_all("article")
        
        for articulo in articulos[:10]:
            # Buscamos el título (h2)
            titulo_element = articulo.query_selector("h2")
            if titulo_element:
                titulo = titulo_element.inner_text()
                
                # Buscamos el link
                link_element = titulo_element.query_selector("a")
                link = link_element.get_attribute("href") if link_element else ""
                
                # Arreglamos links relativos
                if link and link.startswith("/"):
                    link = f"https://elpais.com{link}"
                
                noticias.append({
                    "titulo": titulo,
                    "link": link,
                    # Añadimos una marca para saber que vino por aquí
                    "resumen": "Extraído con Navegador Real (Playwright)"
                })
        
        # 5. Cerramos el navegador para liberar memoria
        browser.close()
        return noticias