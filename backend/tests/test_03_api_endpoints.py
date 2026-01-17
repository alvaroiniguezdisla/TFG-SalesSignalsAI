import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app

# Inicializamos el cliente
client = TestClient(app)

def test_endpoint_get_noticias_estructura():
    """
    OBJETIVO:Verificar que la API responde 200 OK y que el JSON
    tiene los campos que el frontend necesita (titulo, relevancia, ...)
    """
    # 1. Mock de la respuesta de la DB
    mock_db_response = {
        "data": [
            {
                "titulo": "Noticia API Test",
                "url": "http://api-test.com",
                "url_hash": "dummy_hash",
                "fuente": "Test",
                "relevancia_ia": 85,
                "resumen_comercial_ia": "Resumen fake",
                "empresas_clave_ia": ["Empresa A"],
                "publicado_en": "2026-01-01"
            }
        ]
    }

    # objeto que simula el resultado final de .execute()
    result_mock = MagicMock()
    result_mock.data = mock_db_response["data"]

    # 2. Aplicamos el patch a Supabase
    with patch("app.api.endpoints.noticias.supabase") as mock_supabase:
        
        # 3. Configuramos la cadena de llamadas: table -> select -> order -> execute
        # IMPORTANTE: Tiene que coincidir EXACTAMENTE con lo que hace el código real
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = result_mock

        # 4. Ejecutamos la prueba
        response = client.get("/noticias")

        # 5. Verificaciones
        assert response.status_code == 200, f"Error API: {response.text}"
        
        datos = response.json()
        assert isinstance(datos, list)
        assert len(datos) == 1
        
        noticia = datos[0]
        assert noticia["titulo"] == "Noticia API Test"
        assert noticia["relevancia_ia"] == 85
        assert noticia["empresas_clave_ia"] == ["Empresa A"]
        
        print("\n✅ API Integration Test: PASSED")
