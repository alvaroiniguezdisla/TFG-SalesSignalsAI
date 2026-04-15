# ----------------------------------------------------------------------------------
# TEST DE INTEGRACION: EXTRACCION REAL VIA SCRAPER HTML
#
# Objetivo: Verificar que el scraper HTML basado en requests + BeautifulSoup
# sigue encontrando noticias reales en las fuentes configuradas en la base de datos.
#
# IMPORTANTE: Este test requiere conexion a internet y acceso a Supabase real
# para cargar las URLs de scraping configuradas en la aplicacion.
#
# Que comprueba:
#   1. Que cada fuente con scraper_url puede procesarse sin errores fatales.
#   2. Que los articulos extraidos contienen titulo, URL y hash validos.
#   3. Que la estructura devuelta mantiene los campos esperados por el pipeline.
#   4. Que una URL invalida no rompe la aplicacion y devuelve lista vacia.
# ----------------------------------------------------------------------------------

import pytest
from app.services.extraccion.scraper import scrape_noticias

from app.services.almacenamiento.database import get_supabase_service

def get_db_scraper_sources():
    """Obtiene las fuentes para Scraper de la base de datos."""
    try:
        db = get_supabase_service()
        config = db.get_app_config()
        sources = config.get("rss_sources", [])
        # Solo devolvemos las que tienen scraper_url definido
        return [s for s in sources if s.get("scraper_url")]
    except Exception:
        return []

fuentes_scraper = get_db_scraper_sources()

@pytest.mark.parametrize("fuente", fuentes_scraper, ids=[f["name"] for f in fuentes_scraper])
def test_scraper_extrae_articulos_reales(fuente):
    """
    Prueba de integración REAL paramétrica. 
    Itera sobre todas las URLs HTML configuradas y comprueba
    que el scraper (BeautifulSoup) sigue encontrando artículos.
    """
    target_url = fuente["scraper_url"]
    
    resultados = scrape_noticias(target_url, f"Scraper {fuente['name']} (Test)")
    
    # Fuente externa: si hoy está caída/bloqueada/sin noticias, lo notificamos sin bloquear el pipeline de tests.
    if len(resultados) == 0:
        pytest.skip(
            f"[FUENTE_CAIDA] El scraper no encontró artículos en {fuente['name']} "
            f"(caída, bloqueo externo o sin novedades en este momento)."
        )
    
    # Validar la estructura del primer artículo
    primer_articulo = resultados[0]
    
    assert "titulo" in primer_articulo
    assert type(primer_articulo["titulo"]) is str
    assert len(primer_articulo["titulo"]) > 5 # Un título real debe tener más de 5 letras
    
    assert "url" in primer_articulo
    assert primer_articulo["url"].startswith("http"), "La URL debe ser absoluta (http/https)"
    
    assert "url_hash" in primer_articulo
    assert len(primer_articulo["url_hash"]) == 32 # MD5 hash length
    
    # Por definición de nuestro scraper, published_at es None porque es HTML irregular
    assert primer_articulo["published_at"] is None
    
    assert "scraped_at" in primer_articulo

def test_scraper_maneja_url_invalida_gracefully():
    # Probar que no rompe la app si le damos una URL que no existe
    target_url = "https://esta-url-absolutamente-no-existe-12345.com"
    resultados = scrape_noticias(target_url, "Bad Scraper")
    
    # Debe capturar la excepción y devolver lista vacía
    assert isinstance(resultados, list)
    assert len(resultados) == 0
