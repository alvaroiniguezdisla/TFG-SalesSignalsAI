import pytest
from app.services.extraccion.scraper import scrape_noticias
from app.core.config import settings

# Extraer URLs HTML/Scraper configuradas para parametrizar
# Usamos scraper_url de la configuración si la tiene
fuentes_scraper = [{"name": f["name"], "url": f.get("scraper_url", f["url"])} for f in settings.RSS_SOURCES]

@pytest.mark.parametrize("fuente", fuentes_scraper, ids=[f["name"] for f in fuentes_scraper])
def test_scraper_extrae_articulos_reales(fuente):
    """
    Prueba de integración REAL paramétrica. 
    Itera sobre todas las URLs HTML configuradas y comprueba
    que el scraper (BeautifulSoup) sigue encontrando artículos.
    """
    target_url = fuente["url"]
    
    resultados = scrape_noticias(target_url, f"Scraper {fuente['name']} (Test)")
    
    # Asegurarnos de que no nos han bloqueado y la página sigue teniendo artículos
    assert len(resultados) > 0, f"El scraper no encontró artículos en {fuente['name']}. ¿Ha cambiado la estructura HTML o estamos bloqueados?"
    
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
