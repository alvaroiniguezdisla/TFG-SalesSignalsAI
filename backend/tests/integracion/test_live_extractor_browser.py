import pytest
from app.services.extraccion.browser import obtener_noticias_browser
from app.core.config import settings

# Extraer URLs HTML configuradas para parametrizar
# Usamos scraper_url de la configuración si la tiene
fuentes_browser = [{"name": f["name"], "url": f.get("scraper_url", f["url"])} for f in settings.RSS_SOURCES]

@pytest.mark.parametrize("fuente", fuentes_browser, ids=[f["name"] for f in fuentes_browser])
def test_browser_extrae_articulos_reales(fuente):
    """
    Prueba de integración REAL paramétrica. 
    Se conecta a todas las fuentes usando Playwright real (Chromium).
    Verifica que el HTML sigue teniendo <article> o tags equivalentes
    y nuestra heurística de JavaScript no se rompe.
    
    NOTA: Esta prueba es más lenta porque levanta un navegador de verdad por cada iteración.
    """
    target_url = fuente["url"]
    
    resultados = obtener_noticias_browser(target_url, f"Browser {fuente['name']} Test")
    
    # Comprobar que Playwright renderiza la web y encuentra noticias
    assert len(resultados) > 0, f"El browser no encontró artículos en {fuente['name']}. ¿Ha cambiado la estructura o hay un captcha?"
    
    # Validar la estructura del primer artículo
    primer_articulo = resultados[0]
    
    assert "titulo" in primer_articulo
    assert type(primer_articulo["titulo"]) is str
    assert len(primer_articulo["titulo"]) > 5
    
    assert "url" in primer_articulo
    # En browser.py reconstruimos las URLs relativas si hace falta, asi que deben ser absolutas
    assert primer_articulo["url"].startswith("http")
    
    assert "raw_content" in primer_articulo
    assert len(primer_articulo["raw_content"]) > 10 # Asegurarnos que nos trajimos el HTML del articulo
    
    assert primer_articulo["published_at"] is None

def test_browser_maneja_url_invalida_gracefully():
    # Probar que Playwright captura el DNS error sin cerrar la app
    target_url = "https://esta-url-absolutamente-no-existe-12345.com"
    resultados = obtener_noticias_browser(target_url, "Bad Browser")
    
    assert isinstance(resultados, list)
    assert len(resultados) == 0
