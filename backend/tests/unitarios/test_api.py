# ----------------------------------------------------------------------------------
# TEST DE LOS ENDPOINTS DE LA API REST
#
# Objetivo: Verificar que los endpoints de la API devuelven respuestas correctas
# usando el cliente de pruebas de FastAPI (TestClient) y mocks de Supabase.
#
# Que comprueba:
#   1. GET /noticias         -> Devuelve lista de noticias (mock de BD).
#   2. GET /noticias/categorias -> Devuelve categorias del sistema.
#   3. GET /noticias/{hash}  -> Devuelve una noticia concreta (mock de BD).
#   4. GET /noticias/{hash}  -> Devuelve 404 si no existe.
#
# Nota: POST /refrescar no se testea aqui porque ejecuta el pipeline completo,
# que ya esta cubierto por test_pipeline.py.
# ----------------------------------------------------------------------------------

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# --- Datos de prueba reutilizables ---

NOTICIA_FAKE = {
    "id": "uuid-fake-001",
    "titulo": "Empresa X abre nueva sede en Madrid",
    "url": "https://ejemplo.com/noticia-1",
    "url_hash": "abc123hash",
    "fuente": "Diario Test",
    "scraped_at": "2026-01-01T10:00:00",
    "published_at": None,
    "raw_content": "Contenido completo de la noticia...",
    "resumen": "Empresa X se expande.",
    "categoria_ia": "Expansion / Crecimiento",
    "categoria_producto_ia": "Soluciones Empresariales",
    "relevancia_ia": 85,
    "resumen_comercial_ia": "Oportunidad de venta de equipos.",
    "empresas_clave_ia": ["Empresa X"],
    "urls_extra": []
}


# --- Tests del endpoint GET /noticias ---

@patch("app.api.endpoints.noticias.supabase")
def test_obtener_noticias_devuelve_lista(mock_supabase):
    """
    Verifica que GET /noticias devuelve una lista de noticias.
    Este es el endpoint principal que consume el frontend.
    """
    # Simulamos que Supabase devuelve una noticia
    mock_response = MagicMock()
    mock_response.data = [NOTICIA_FAKE]
    mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

    response = client.get("/noticias")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["titulo"] == "Empresa X abre nueva sede en Madrid"
    assert data[0]["relevancia_ia"] == 85


@patch("app.api.endpoints.noticias.supabase")
def test_obtener_noticias_lista_vacia(mock_supabase):
    """
    Verifica que GET /noticias devuelve una lista vacia
    cuando no hay noticias en la base de datos.
    """
    mock_response = MagicMock()
    mock_response.data = []
    mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response

    response = client.get("/noticias")

    assert response.status_code == 200
    assert response.json() == []


# --- Tests del endpoint GET /noticias/categorias ---

def test_obtener_categorias():
    """
    Verifica que el endpoint devuelve las categorias oficiales del sistema.
    No necesita mock porque no toca la base de datos.
    """
    response = client.get("/noticias/categorias")

    assert response.status_code == 200

    data = response.json()
    assert "signals" in data
    assert "products" in data
    assert len(data["signals"]) > 0
    assert len(data["products"]) > 0

    # Verificar que las categorias conocidas estan presentes
    assert "Expansión / Crecimiento " in data["signals"]
    assert "Gaming / OMEN" in data["products"]


# --- Tests del endpoint GET /noticias/{url_hash} ---

@patch("app.api.endpoints.noticias.supabase")
def test_obtener_noticia_por_hash(mock_supabase):
    """
    Verifica que buscar una noticia por su hash devuelve
    la noticia correcta con codigo 200.
    """
    mock_response = MagicMock()
    mock_response.data = [NOTICIA_FAKE]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

    response = client.get("/noticias/abc123hash")

    assert response.status_code == 200
    data = response.json()
    assert data["url_hash"] == "abc123hash"
    assert data["titulo"] == "Empresa X abre nueva sede en Madrid"


@patch("app.api.endpoints.noticias.supabase")
def test_noticia_no_encontrada(mock_supabase):
    """
    Verifica que buscar una noticia con un hash inexistente
    devuelve un error 404 con mensaje descriptivo.
    """
    mock_response = MagicMock()
    mock_response.data = []
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

    response = client.get("/noticias/hash_que_no_existe")

    assert response.status_code == 404
    assert "no encontrada" in response.json()["detail"].lower()
