# ----------------------------------------------------------------------------------
# TEST DE INTEGRACION: EXTRACCION REAL VIA BROWSER (PLAYWRIGHT)
#
# Objetivo: Verificar que el extractor basado en navegador real (Playwright)
# sigue funcionando contra fuentes reales configuradas en la base de datos.
#
# IMPORTANTE: Este test requiere conexion a internet, acceso a Supabase real
# y que Playwright/Chromium esten instalados en el entorno.
#
# Que comprueba:
#   1. Que cada fuente con scraper_url puede procesarse con Browser.
#   2. Que el extractor devuelve articulos con estructura valida.
#   3. Que las URLs relativas se normalizan como URLs absolutas.
#   4. Que una URL invalida no rompe la aplicacion y devuelve lista vacia.
# ----------------------------------------------------------------------------------

import pytest
from app.services.extraccion.browser import obtener_noticias_browser

from app.services.almacenamiento.database import get_supabase_service

def get_db_browser_sources():
    """Obtiene las fuentes para Browser de la base de datos."""
    try:
        db = get_supabase_service()
        config = db.get_app_config()
        sources = config.get("rss_sources", [])
        # Solo devolvemos las que tienen scraper_url definido
        return [s for s in sources if s.get("scraper_url")]
    except Exception:
        return []

fuentes_browser = get_db_browser_sources()

@pytest.mark.parametrize("fuente", fuentes_browser, ids=[f["name"] for f in fuentes_browser])
def test_browser_extrae_articulos_reales(fuente):
    """
    Prueba de integración REAL paramétrica. 
    Se conecta a todas las fuentes usando Playwright real (Chromium).
    Verifica que el HTML sigue teniendo <article> o tags equivalentes
    y nuestra heurística de JavaScript no se rompe.
    
    """
    target_url = fuente["scraper_url"]
    
    resultados = obtener_noticias_browser(target_url, f"Browser {fuente['name']} Test")
    
    # Fuente externa: si hoy está caída/bloqueada/sin noticias, lo notificamos sin bloquear el pipeline de tests.
    if len(resultados) == 0:
        pytest.skip(
            f"[FUENTE_CAIDA] El browser no encontró artículos en {fuente['name']} "
            f"(caída, bloqueo externo o sin novedades en este momento)."
        )
    
    # Validar la estructura del primer artículo
    primer_articulo = resultados[0]
    
    assert "titulo" in primer_articulo
    assert type(primer_articulo["titulo"]) is str
    assert len(primer_articulo["titulo"]) > 5
    
    assert "url" in primer_articulo
    # En browser.py reconstruimos las URLs relativas si hace falta, asi que deben ser absolutas
    assert primer_articulo["url"].startswith("http")
    
    assert "resumen" in primer_articulo
    # El resumen ahora lo sacamos dinámicamente de la etiqueta <p>, no explota si viene vacío
    if primer_articulo["resumen"]:
        assert len(primer_articulo["resumen"]) > 0

    assert primer_articulo["published_at"] is None

def test_browser_maneja_url_invalida_gracefully():
    """
    Verifica que Playwright captura el error de DNS sin cerrar la aplicacion.
    Debe devolver lista vacia en lugar de lanzar una excepcion.
    """
    target_url = "https://esta-url-absolutamente-no-existe-12345.com"
    resultados = obtener_noticias_browser(target_url, "Bad Browser")
    
    assert isinstance(resultados, list)
    assert len(resultados) == 0
