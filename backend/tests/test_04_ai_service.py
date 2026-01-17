import pytest 
import json 
from unittest.mock import MagicMock, patch
from app.services.inteligencia.llm_clasificacion_noticias import LlmService

def test_ia_analisis_formato_correcto():
    """
    OBJETIVO: Verificar que el servicio de IA clasifica correctamente
    en las categorias que queremos(simulamos la respuestra de Ollama con 
    un Mock)
    """

    # 1. Mock de la respuesta de Ollama
    respuesta_ollama_simulada = {
        "categoria": "Expansión / Crecimiento ",
        "relevancia": 90,
        "resumen_comercial": "El cliente va a contratar 400 ingenieros.",
        "empresas": ["Glovo", "Google"]
    }

    #2. MOCK DE OLLAMA- ollama devuelve diccionarios anidados 
    mock_response ={
        'message' :{
            'content': json.dumps(respuesta_ollama_simulada)
        }
    }

    
    #3. Aplicamos el patch a Ollama
    with patch("app.services.inteligencia.llm_clasificacion_noticias.ollama.chat") as mock_chat:
        mock_chat.return_value = mock_response

        #4. Ejecutamos
        llm_service = LlmService()
        resultado = llm_service.analizar_oportunidad("Glovo crece", "Texto de prueba...")

        #5. Verificaciones
        assert resultado["categoria"] == "Expansión / Crecimiento "
        assert resultado["relevancia"] == 90
        assert resultado["resumen_comercial"] == "El cliente va a contratar 400 ingenieros."
        assert resultado["empresas"] == ["Glovo", "Google"]

        print("Test 04 AI Service: PASSED")
        