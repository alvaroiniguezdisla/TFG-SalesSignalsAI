# ----------------------------------------------------------------------------------
# TEST DE INTEGRACION: EXTRACCION REAL VIA RSS
#
# Objetivo: Verificar que los feeds RSS reales configurados en la base de datos
# siguen siendo compatibles con nuestro extractor y mantienen la estructura esperada.
#
# IMPORTANTE: Este test requiere conexion a internet y acceso a Supabase real
# para recuperar las fuentes RSS configuradas en la aplicacion.
#
# Que comprueba:
#   1. Que cada feed RSS configurado puede consultarse correctamente.
#   2. Que los articulos extraidos contienen los campos minimos esperados.
#   3. Que published_at llega informado en las fuentes RSS reales.
#   4. Que una URL RSS invalida no rompe la aplicacion y devuelve lista vacia.
# ----------------------------------------------------------------------------------

import pytest
from app.services.extraccion.rss import obtener_noticias_rss

from app.services.almacenamiento.database import get_supabase_service

def get_db_rss_sources():
    """Obtiene las fuentes RSS de la base de datos para los tests."""
    try:
        db = get_supabase_service()
        config = db.get_app_config()
        return config.get("rss_sources", [])
    except Exception:
        return []

fuentes_rss = get_db_rss_sources()

@pytest.mark.parametrize("fuente", fuentes_rss, ids=[f["name"] for f in fuentes_rss])
def test_rss_extrae_noticias_reales(fuente):
    """
    Prueba de integración REAL paramétrica. 
    Itera sobre todos los feeds RSS configurados en la base de datos y comprueba
    que la estructura del XML de las webs no ha cambiado.
    """
    resultados = obtener_noticias_rss(fuente["url"], fuente["name"])
    
    # Fuente externa: si hoy está caída/bloqueada/sin noticias, lo notificamos sin bloquear el pipeline de tests.
    if len(resultados) == 0:
        pytest.skip(
            f"[FUENTE_CAIDA] El feed RSS {fuente['name']} no devolvió artículos "
            f"(caída, bloqueo externo o sin novedades en este momento)."
        )
    
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
    """
    Verifica que el extractor RSS no lanza una excepcion si la URL es invalida
    o el servidor no existe. Debe devolver una lista vacia sin romper la app.
    """
    target_url = "https://esta-url-absolutamente-no-existe-12345.com/rss.xml"
    resultados = obtener_noticias_rss(target_url, "Bad RSS")
    
    assert isinstance(resultados, list)
    assert len(resultados) == 0
