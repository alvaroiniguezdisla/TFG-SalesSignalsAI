from playwright.sync_api import sync_playwright
from typing import List, Dict
import hashlib
from datetime import datetime



def hash_url(url:str) -> str:
    return hashlib.md5(url.encode('utf-8')).hexdigest()

def obtener_noticias_browser(target_url: str, nombre_fuente: str="Browser Genérico") -> List[Dict[str, str]]:
    # "sync_playwright" es el gestor que arranca la maquinaria
    with sync_playwright() as p:
        # 1. Lanzamos un navegador Chromium
        # headless=True significa "sin cabeza" (invisible). 
        # Si ponemos  False, veremos el navegador abrirse en la pantalla
        browser = p.chromium.launch(headless=True)
        
        # 2. Abrimos una pestaña nueva
        page = browser.new_page()
        
        # 3. Vamos a la web
        page.goto(target_url)
        
        # 4. Esperamos a que cargue el main
        page.wait_for_selector("main")
        
        noticias = []
        # Seleccionamos todos los artículos DENTRO DE MAIN
        # Primero buscamos el main
        main_element = page.query_selector("main")
        if main_element:
            articulos = main_element.query_selector_all("article")
            # FALLBACK: Si no hay artículos en main, buscamos contenedores de títulos
            if not articulos:
                # Buscamos h2 directamente que tengan enlace
                titulos_h2 = main_element.query_selector_all("h2:has(a)")
                # Usamos el propio h2 como "artículo" o su padre
                articulos = [h2 for h2 in titulos_h2]
        else:
            articulos = page.query_selector_all("article")
        
        for articulo in articulos[:10]:
            # Si es un <article>, buscamos h2 dentro. Si ya es un h2, usamos ese mismo.
            tagName = articulo.evaluate("el => el.tagName")
            if tagName == "H2":
                titulo_element = articulo
            else:
                titulo_element = articulo.query_selector("h2") or articulo.query_selector("h3")
            
            if titulo_element:
                titulo = titulo_element.inner_text()
                
                # Buscamos el link
                link_element = titulo_element.query_selector("a")
                link = link_element.get_attribute("href") if link_element else ""
                
                # Arreglamos links relativos 
                if link and link.startswith("/"):
                    # Reconstruimos dominio base: protocol://domain.com
                    domain = "/".join(target_url.split("/")[:3])
                    link = f"{domain}{link}"
                
                url_completa = link
                
                noticias.append({
                    "url": url_completa,
                    "url_hash": hash_url(url_completa),
                    "titulo": titulo,
                    "fuente": nombre_fuente,
                    "raw_content": str(articulo.inner_html()), # Guardamos el HTML interno del articulo
                    "resumen": "Extraído con Navegador Real (Playwright)",
                    "scraped_at": datetime.now().isoformat()
                })
        
        # 5. Cerramos el navegador para liberar memoria
        browser.close()
        return noticias