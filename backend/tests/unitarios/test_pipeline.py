# ----------------------------------------------------------------------------------
# TEST DEL PIPELINE COMPLETO (SIMULACION CON MOCKS)
#
# Objetivo: Verificar que el flujo completo (Extraccion -> IA -> Base de Datos)
# funciona correctamente usando datos simulados para no depender de servicios
# externos (Ollama, Supabase, internet).
#
# Que comprueba:
#   1. Que el extractor se ejecuta y obtiene noticias.
#   2. Que la IA analiza todas las noticias (con y sin raw_content).
#   3. Que si no hay noticias, el pipeline se detiene sin llamar a la IA.
#   4. Que si la IA falla, la noticia se guarda con campos de error.
# ----------------------------------------------------------------------------------

from unittest.mock import MagicMock, patch
import sys

# Mock de ollama para evitar error de importacion si no esta instalado.
# Ollama se importa dentro de LlmService, y si no existe en el sistema,
# Python peta al importar pipeline.py (ni siquiera llega a ejecutar el test).
sys.modules["ollama"] = MagicMock()

from app.services.orquestacion.pipeline import NewsPipeline


# --- Datos de prueba reutilizables ---

NOTICIA_CON_HTML = {
    "titulo": "Noticia Con Contenido HTML",
    "raw_content": "<html><body><p>Texto largo de prueba con mas de "
                    "cincuenta caracteres para que pase el filtro.</p>"
                    "</body></html>",
    "fuente": "Diario Test",
    "url": "http://example.com/noticia1",
    "url_hash": "hash123456"
}

NOTICIA_SIN_CONTENIDO = {
    "titulo": "Noticia Sin Contenido",
    "raw_content": "",
    "fuente": "Diario Test",
    "url": "http://example.com/noticia2",
    "url_hash": "hash789012",
    "resumen": "Resumen de prueba para fallback"
}

RESPUESTA_IA_FAKE = {
    "categoria": "Expansion / Crecimiento",
    "categoria_producto": "Soluciones Empresariales",
    "relevancia": 90,
    "resumen_comercial": "Oportunidad detectada",
    "empresas": [{"nombre": "Empresa Test", "tamano": "Gran Cuenta"}],
    "talk_track": "- Punto de conversacion 1\n- Punto de conversacion 2",
    "email_draft": "Asunto: Oportunidad\n\nEstimado..."
}


# --- Tests ---

@patch("app.services.orquestacion.pipeline.get_extractor_manager")
@patch("app.services.orquestacion.pipeline.LlmService")
@patch("app.services.orquestacion.pipeline.SupabaseService")
def test_ejecucion_completa(MockDB, MockLLM, MockGetExtractor):
    """
    Simula el pipeline con 2 noticias: una con HTML y otra sin contenido.
    Verifica que ambas pasan por la IA y se guardan en la base de datos
    con los campos enriquecidos correctamente.
    """
    MockGetExtractor.return_value.obtener_noticias.return_value = [NOTICIA_CON_HTML, NOTICIA_SIN_CONTENIDO]

    mock_llm = MockLLM.return_value
    mock_llm.analizar_oportunidad.return_value = RESPUESTA_IA_FAKE

    mock_db = MockDB.return_value

    pipeline = NewsPipeline()
    pipeline.ejecutar()

    # El extractor se llamo una vez
    MockGetExtractor.return_value.obtener_noticias.assert_called_once()

    # La IA analizo las 2 noticias (la vacia usa fallback titulo+resumen)
    assert mock_llm.analizar_oportunidad.call_count == 2

    # Se guardo en base de datos una vez
    mock_db.insert_news_deduplicacion.assert_called_once()

    # Verificar que las noticias tienen los campos de IA
    noticias_guardadas = mock_db.insert_news_deduplicacion.call_args[0][0]
    assert len(noticias_guardadas) == 2
    assert noticias_guardadas[0]["categoria_ia"] == "Expansion / Crecimiento"
    assert noticias_guardadas[0]["relevancia_ia"] == 90
    assert noticias_guardadas[0]["empresas_clave_ia"] == ["Empresa Test"]
    assert noticias_guardadas[0]["empresas_detalle_ia"] == [{"nombre": "Empresa Test", "tamano": "Gran Cuenta"}]
    assert noticias_guardadas[0]["talk_track_ia"] != ""
    assert noticias_guardadas[0]["email_draft_ia"] != ""


@patch("app.services.orquestacion.pipeline.get_extractor_manager")
@patch("app.services.orquestacion.pipeline.LlmService")
@patch("app.services.orquestacion.pipeline.SupabaseService")
def test_pipeline_sin_noticias(MockDB, MockLLM, MockGetExtractor):
    """
    Si el scraper no encuentra noticias (internet caido, fuentes sin novedades),
    el pipeline debe detenerse inmediatamente sin llamar a la IA ni a la BD.
    """
    MockGetExtractor.return_value.obtener_noticias.return_value = []

    pipeline = NewsPipeline()
    pipeline.ejecutar()

    MockGetExtractor.return_value.obtener_noticias.assert_called_once()
    MockLLM.return_value.analizar_oportunidad.assert_not_called()
    MockDB.return_value.insert_news_deduplicacion.assert_not_called()


@patch("app.services.orquestacion.pipeline.get_extractor_manager")
@patch("app.services.orquestacion.pipeline.LlmService")
@patch("app.services.orquestacion.pipeline.SupabaseService")
def test_pipeline_ia_falla(MockDB, MockLLM, MockGetExtractor):
    """
    Si la IA falla (Ollama caido, modelo no responde), el pipeline no debe
    romper. La noticia se guarda con campos de error ('Error IA', relevancia 0).
    """
    MockGetExtractor.return_value.obtener_noticias.return_value = [NOTICIA_CON_HTML]

    # La IA devuelve None (fallo)
    mock_llm = MockLLM.return_value
    mock_llm.analizar_oportunidad.return_value = None

    mock_db = MockDB.return_value

    pipeline = NewsPipeline()
    pipeline.ejecutar()

    # La noticia se guardo a pesar del fallo de la IA
    mock_db.insert_news_deduplicacion.assert_called_once()

    noticias_guardadas = mock_db.insert_news_deduplicacion.call_args[0][0]
    assert len(noticias_guardadas) == 1
    assert noticias_guardadas[0]["categoria_ia"] == "Error IA"
    assert noticias_guardadas[0]["relevancia_ia"] == 0
