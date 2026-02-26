from playwright.sync_api import sync_playwright
from typing import List, Dict, Any
from datetime import datetime

import logging
from app.core.utils import hash_url

logger = logging.getLogger(__name__)

def obtener_noticias_browser(target_url: str, nombre_fuente: str="Browser Genérico") -> List[Dict[str, Any]]:
    logger.info(f"[EXTRACCION_BROWSER] Emulando navegador headless para {target_url} ({nombre_fuente})")
    try:
        with sync_playwright() as p:
            # 1. Lanzamos un navegador Chromium
            browser = p.chromium.launch(headless=True)
            
            # 2. Abrimos una pestaña nueva CON USER AGENT REAL (para evitar bloqueos tipo Akamai)
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            page = browser.new_page(user_agent=user_agent, viewport={'width': 1280, 'height': 800})
            
            # 3. Vamos a la web
            # Usamos wait_until="networkidle" para asegurar que carguen los scripts de Akamai/Cloudflare
            page.goto(target_url, wait_until="networkidle", timeout=60000)
            
            # 4. Esperamos a que cargue el main
            page.wait_for_selector("main")
            
            noticias = []
            # Seleccionamos todos los artículos DENTRO DE MAIN
            # Primero buscamos el main
            main_element = page.query_selector("main")
            if main_element:
                # El Economista usa 'div.articleContent' o 'div.articleHeadline' en lugar de 'article'
                articulos = main_element.query_selector_all("article, .articleContent, .articleHeadline")
                # FALLBACK: Si no hay artículos en main, buscamos contenedores de títulos
                if not articulos:
                    # Buscamos h2 directamente que tengan enlace
                    titulos_h2 = main_element.query_selector_all("h2:has(a), h3:has(a)")
                    articulos = [h2 for h2 in titulos_h2]
            else:
                articulos = page.query_selector_all("article, .articleContent")
            
            for articulo in articulos[:15]:
                # Si es un <article> o div, buscamos h2/h3 dentro. Si ya es un h2, usamos ese mismo.
                tagName = articulo.evaluate("el => el.tagName")
                if tagName == "H2":
                    titulo_element = articulo
                else:
                    titulo_element = articulo.query_selector("h2") or articulo.query_selector("h3")
                
                if titulo_element:
                    titulo = titulo_element.inner_text()
                    
                    # Buscamos el link interno al titulo
                    link_element = titulo_element.query_selector("a")
                    link = link_element.get_attribute("href") if link_element else ""
                    
                    # FALLBACK: A veces el titulo (h2) esta envuelto por el tag <a> (ej. Expansion)
                    if not link:
                        parent_is_a = titulo_element.evaluate("el => el.parentElement && el.parentElement.tagName === 'A'")
                        if parent_is_a:
                            link = titulo_element.evaluate("el => el.parentElement.getAttribute('href')")
                    
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
                        "raw_content": str(articulo.inner_html()),
                        "resumen": "Extraído con Navegador Real (Playwright)",
                        "published_at": None,
                        "scraped_at": datetime.now().isoformat()
                    })
            
            # 5. Cerramos el navegador para liberar memoria
            browser.close()
            return noticias
    except Exception as e:
        logger.error(f"[EXTRACCION_BROWSER] Error fatal emulando DOM en {target_url}: {e}")
        return []