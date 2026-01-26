# ----------------------------------------------------------------------------------
# TEST DEL PIPELINE COMPLETO (SIMULACRO)
# Qué hace esto: Prueba todo el proceso (Descarga -> IA -> Base de Datos) pero usando
# datos falsos ("Mocks") para no gastar dinero en la IA ni ensuciar la base de datos.
# Para qué sirve: Para asegurar que las piezas encajan bien antes de probar con fuego real.
# ----------------------------------------------------------------------------------

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Esto es un truco para mocking de ollama si no esta instalado
sys.modules["ollama"] = MagicMock()

# Importamos las clases a testear
from app.services.orquestacion.pipeline import NewsPipeline

class TestPipeline(unittest.TestCase):
    
    # Usamos patch para no llamar a las 3 partes reales del sistema
    @patch('app.services.orquestacion.pipeline.extractor')
    @patch('app.services.orquestacion.pipeline.LlmService')
    @patch('app.services.orquestacion.pipeline.SupabaseService')
    def test_ejecucion_completa(self, MockDB, MockLLM, MockExtractor):
        
        # 1. Preparamos datos falsos para el extractor
        mock_noticias = [
            {
                'titulo': 'Noticia Buena', 
                'raw_content': 'Texto suficientemente largo para que la IA lo procese bien.', 
                'fuente': 'Test', 
                'url': 'http://test.com/1'
            },
            {
                'titulo': 'Noticia Vacia', 
                'raw_content': '', # Esta deberia filtrarse
                'fuente': 'Test', 
                'url': 'http://test.com/2'
            },
        ]
        MockExtractor.obtener_noticias.return_value = mock_noticias

        # 2. Preparamos la respuesta falsa del LLM
        mock_llm_instance = MockLLM.return_value
        mock_llm_instance.analizar_oportunidad.return_value = {
            'categoria': 'Test', 
            'relevancia': 80, 
            'resumen_comercial': 'Oportunidad', 
            'empresas': ['Empresa Test']
        }

        # 3. DB Mock
        mock_db_instance = MockDB.return_value

        # 4. Lanzamos el pipeline
        pipeline = NewsPipeline()
        pipeline.ejecutar()

        # 5. Comprobamos cosas
        
        # Se llamo al extractor?
        MockExtractor.obtener_noticias.assert_called_once()
        
        # Se llamo a la IA? (Solo 1 vez porque la otra noticia estaba vacia)
        mock_llm_instance.analizar_oportunidad.assert_called_once()
        
        # Se guardo en base de datos?
        mock_db_instance.insert_news_deduplicacion.assert_called_once()
        
        # Verificamos que lo que se mando a guardar es correcto
        args, _ = mock_db_instance.insert_news_deduplicacion.call_args
        noticias_finales = args[0]
        
        self.assertEqual(len(noticias_finales), 1)
        self.assertEqual(noticias_finales[0]['titulo'], 'Noticia Buena')
        
if __name__ == '__main__':
    unittest.main()
