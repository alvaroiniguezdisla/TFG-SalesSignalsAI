# ----------------------------------------------------------------------------------
# TEST DE LOS ENDPOINTS DE ADMINISTRACION
#
# Objetivo: Verificar que los endpoints del panel de administracion devuelven
# respuestas correctas usando mocks del servicio de base de datos.
#
# Que comprueba:
#   1. GET /api/admin/config   -> Devuelve la configuracion global del sistema.
#   2. GET /api/admin/users    -> Devuelve la lista de usuarios registrados.
#   3. GET /api/admin/metrics  -> Devuelve los KPIs del sistema.
#   4. GET /api/admin/config   -> Devuelve 404 si no hay configuracion en BD.
# ----------------------------------------------------------------------------------

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.almacenamiento.database import get_supabase_service

client = TestClient(app)


# --- Datos de prueba reutilizables ---

CONFIG_FAKE = {
    "umbral_similitud": 0.85,
    "ollama_model": "llama3.1",
    "ai_prompt": "Analiza la siguiente noticia...",
    "ai_prompt_default": "",
    "rss_sources": []
}

USUARIOS_FAKE = [
    {
        "id": "uuid-user-001",
        "email": "usuario1@empresa.com",
        "first_name": "Ana",
        "last_name": "Garcia",
        "role": "user",
        "favorite_companies": ["Santander"],
        "favorite_categories": ["Expansion / Crecimiento"]
    }
]

METRICAS_FAKE = {
    "total_users": 5,
    "active_users_30d": 3,
    "total_news": 120,
    "news_7d": 18,
    "total_feedbacks": 40,
    "likes_count": 30,
    "dislikes_count": 10,
    "active_sources": 4
}


# --- Tests ---

def test_obtener_config_admin():
    """
    Verifica que GET /api/admin/config devuelve la configuracion global
    con los campos esperados del sistema.
    """
    mock_service = MagicMock()
    mock_service.get_app_config.return_value = CONFIG_FAKE.copy()

    app.dependency_overrides[get_supabase_service] = lambda: mock_service

    response = client.get("/api/admin/config")

    assert response.status_code == 200
    data = response.json()
    assert data["ollama_model"] == "llama3.1"
    assert data["umbral_similitud"] == 0.85
    assert "ai_prompt" in data

    app.dependency_overrides.clear()


def test_obtener_config_admin_no_encontrada():
    """
    Verifica que GET /api/admin/config devuelve 404
    si no hay configuracion guardada en la base de datos.
    """
    mock_service = MagicMock()
    mock_service.get_app_config.return_value = None

    app.dependency_overrides[get_supabase_service] = lambda: mock_service

    response = client.get("/api/admin/config")

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_obtener_usuarios_admin():
    """
    Verifica que GET /api/admin/users devuelve la lista completa
    de perfiles de usuario registrados en el sistema.
    """
    mock_service = MagicMock()
    mock_service.obtener_usuarios_preferencias.return_value = USUARIOS_FAKE

    app.dependency_overrides[get_supabase_service] = lambda: mock_service

    response = client.get("/api/admin/users")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["email"] == "usuario1@empresa.com"

    app.dependency_overrides.clear()


def test_obtener_metricas_admin():
    """
    Verifica que GET /api/admin/metrics devuelve los KPIs del sistema
    con todos los campos numericos esperados.
    ```
    """
    mock_service = MagicMock()
    mock_service.get_admin_metrics.return_value = METRICAS_FAKE

    app.dependency_overrides[get_supabase_service] = lambda: mock_service

    response = client.get("/api/admin/metrics")

    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] == 5
    assert data["total_news"] == 120
    assert data["likes_count"] == 30
    assert data["dislikes_count"] == 10

    app.dependency_overrides.clear()

