import pytest
from app.services.extraccion.rss import obtener_noticias_rss
from app.core.config import settings

# Extraer fuentes RSS configuradas para parametrizar
fuentes_rss = [f for f in settings.RSS_SOURCES if f.get("type") == "rss"]

@pytest.mark.parametrize("fuente", fuentes_rss, ids=[f["name"] for f in fuentes_rss])
def test_rss_extrae_noticias_reales(fuente):
    """
    Prueba de integración REAL paramétrica. 
    Itera sobre todos los feeds RSS configurados en .env y comprueba
    que la estructura del XML de las webs no ha cambiado.
    """
    resultados = obtener_noticias_rss(fuente["url"], fuente["name"])
    
    # Comprobar que el feed de verdad devolvió artículos y no fuimos bloqueados
    assert len(resultados) > 0, f"El feed RSS {fuente['name']} no ha devuelto artículos."
    
    # Validar la estructura del primer artículo
    primer_articulo = resultados[0]
    
    assert "titulo" in primer_articulo
    assert type(primer_articulo["titulo"]) is str
    assert len(primer_articulo["titulo"]) > 5
    
    assert "url" in primer_articulo
    assert primer_articulo["url"].startswith("http")
    
    assert primer_articulo["fuente"] == fuente["name"]
    
    # RSS es la unica fuente donde sí deberíamos poder extraer published_at
    assert primer_articulo["published_at"] is not None
    assert isinstance(primer_articulo["published_at"], str)

def test_rss_maneja_url_invalida_gracefully():
    # Probar que no rompe la app si le damos un RSS malo
    target_url = "https://esta-url-absolutamente-no-existe-12345.com/rss.xml"
    resultados = obtener_noticias_rss(target_url, "Bad RSS")
    
    assert isinstance(resultados, list)
    assert len(resultados) == 0
