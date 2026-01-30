import sys
import os
import unittest
from unittest.mock import MagicMock, patch


sys.modules["ollama"] = MagicMock()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.orquestacion.pipeline import NewsPipeline

class TestFullPipeline(unittest.TestCase):
    
    @patch('app.services.orquestacion.pipeline.extractor')
    @patch('app.services.orquestacion.pipeline.LlmService')
    @patch('app.services.orquestacion.pipeline.SupabaseService')
    def test_pipeline_execution(self, MockDB, MockLLM, MockExtractor):
        print("\n--- Iniciando Test del Pipeline ---")

        # 1. Mock Extractor
        mock_noticias = [
            {
                'titulo': 'Noticia Relevante de Prueba', 
                'raw_content': '<html><body><p>Texto largo de prueba con mas de cincuenta caracteres para que pase el filtro de validacion.</p></body></html>', 
                'fuente': 'Diario Test', 
                'url': 'http://example.com/noticia1'
            },
            {
                'titulo': 'Noticia Vacia', 
                'raw_content': '', 
                'fuente': 'Diario Test', 
                'url': 'http://example.com/vacia'
            },
        ]
        MockExtractor.obtener_noticias.return_value = mock_noticias

        # 2. Mock LLM
        mock_llm_instance = MockLLM.return_value
        mock_llm_instance.analizar_oportunidad.return_value = {
            'categoria': 'Test Estrategico', 
            'relevancia': 90, 
            'resumen_comercial': 'Oportunidad detectada', 
            'empresas': ['Empresa Test']
        }

        # 3. Mock DB
        mock_db_instance = MockDB.return_value

        # 4. Ejecutar logica
        pipeline = NewsPipeline()
        pipeline.ejecutar()

        # 5. Validaciones
        MockExtractor.obtener_noticias.assert_called_once()
        print("1. Extraccion ejecutada correctamente.")

        # Verificar LLM llamado solo 1 vez (filtro de vacios funciona)
        mock_llm_instance.analizar_oportunidad.assert_called_once()
        print("2. Analisis IA ejecutado solo para noticias validas.")

        # Verificar DB
        mock_db_instance.insert_news_deduplicacion.assert_called_once()
        args, _ = mock_db_instance.insert_news_deduplicacion.call_args
        noticias_insertadas = args[0]
        
        self.assertEqual(len(noticias_insertadas), 1)
        self.assertEqual(noticias_insertadas[0]['titulo'], 'Noticia Relevante de Prueba')
        self.assertEqual(noticias_insertadas[0]['categoria_ia'], 'Test Estrategico')
        print("3. Insercion en Base de Datos llamada con datos procesados.")
        
        print("--- Test Finalizado con Exito ---")

if __name__ == '__main__':
    unittest.main()
