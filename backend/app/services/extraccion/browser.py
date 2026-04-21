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
            
            # 4. Esperamos a que el cuerpo de la página esté disponible
            page.wait_for_selector("body")
            
            noticias = []
            
            # BUSCAMOS SOLO EN <main> PARA EVITAR EL "TICKER" DE POLITICA DEL HEADER
            contenedor = page.query_selector("main")
            if not contenedor:
                contenedor = page.query_selector("body") # Fallback por si acaso
                
            # Búsqueda semántica universal de artículos
            articulos = contenedor.query_selector_all("article")
            
            # SI NO HAY ARTICULOS SEMÁNTICOS (Estrategia Fallback interna)
            if not articulos:
                # Estrategia alternativa: Buscar encabezados y tratar a su contenedor padre como artículo
                titulares = contenedor.query_selector_all("h2, h3")
                articulos = []
                for t in titulares:
                    # Filtramos los que tengan enlace y subimos a su contenedor padre (emulando t.parent de BeautifulSoup)
                    if t.query_selector("a"):
                        padre = t.evaluate_handle("el => el.parentElement").as_element()
                        if padre:
                            articulos.append(padre)
            
            for articulo in articulos[:15]:
                # 1. Buscamos el nodo del título (Prioridad h1/h2/h3/h4)
                # Si entramos por el fallback interno, 'articulo' podría ser el propio H2
                tagName = articulo.evaluate("el => el.tagName").upper()
                if tagName in ["H1", "H2", "H3", "H4"]:
                    titulo_nodo = articulo
                else:
                    titulo_nodo = articulo.query_selector("h1, h2, h3, h4")
                
                etiqueta_link = None
                titulo = ""

                # 2. Localización del elemento de hipervínculo (<a>)
                if titulo_nodo and titulo_nodo.query_selector("a"):
                    # Estructura estándar: El enlace se encuentra anidado en el titular (ej. <h2><a>Titular</a></h2>)
                    etiqueta_link = titulo_nodo.query_selector("a")
                elif titulo_nodo and articulo.evaluate("(el) => el.parentElement && el.parentElement.tagName === 'A'", arg=titulo_nodo):
                    # Estructura invertida: El titular está envuelto por el enlace (ej. <a><h2>Titular</h2></a>)
                    # Mediante evaluate_handle se accede al elemento padre en el DOM
                    etiqueta_link = articulo.evaluate_handle("(el) => el.parentElement", arg=titulo_nodo).as_element()
                else:
                    # Estrategia de Fallback: Selección del primer enlace genérico del contenedor si carece de estructura estándar
                    etiqueta_link = articulo.query_selector("a")

                # 3. Extracción de atributos textuales y construcción del objeto
                if etiqueta_link:
                    href = etiqueta_link.get_attribute("href")
                    titulo = etiqueta_link.inner_text().strip()
                    
                    # A veces el <a> es bloque estructural e inner_text falla, pillamos el texto del H2 si lo hay
                    if not titulo and titulo_nodo:
                        titulo = titulo_nodo.inner_text().strip()
                        
                    # Validación de seguridad: tiene que ser un enlace real con texto viable
                    if href and titulo and len(titulo) > 5:
                        # Arreglamos links relativos 
                        if href.startswith("/"):
                            domain = "/".join(target_url.split("/")[:3])
                            href = f"{domain}{href}"
                        
                        url_completa = href
                        
                        # Intento de extraer resumen buscando la primera etiqueta de párrafo (<p>)
                        p_element = articulo.query_selector("p")
                        resumen_texto = p_element.inner_text().strip() if p_element else ""
                        
                        noticias.append({
                            "url": url_completa,
                            "url_hash": hash_url(url_completa),
                            "titulo": titulo,
                            "fuente": nombre_fuente,
                            "resumen": resumen_texto,
                            "published_at": None,
                            "scraped_at": datetime.now().isoformat()
                        })
            
            # 5. Cerramos el navegador para liberar memoria
            browser.close()
            return noticias
    except Exception as e:
        logger.error(f"[EXTRACCION_BROWSER] Error fatal emulando DOM en {target_url}: {e}")
        return []