"""
Test del Manager de Extracción con Fallback
Verifica que el sistema hace fallback correctamente de RSS → Scraper → Browser
"""
from unittest.mock import MagicMock, patch
from app.services.extraccion.manager import NewsExtractorManager

def test_fallback_rss_to_scraper():
    """
    Test: Simula que el RSS devuelve vacío y verifica que el Scraper toma el relevo.
    """
    
    # Noticia dummy que devolverá el scraper
    dummy_news = [{"titulo": "Noticia Test", "url": "http://test.com", "fuente": "Test"}]
    
    # Mock: RSS devuelve vacío, Scraper devuelve noticias
    mock_rss = MagicMock(return_value=[])
    mock_scraper = MagicMock(return_value=dummy_news)
    mock_browser = MagicMock(return_value=[])  # No se debería llamar
    
    # Parcheamos las funciones donde se USAN (en el módulo manager)
    with patch('app.services.extraccion.manager.obtener_noticias_rss', mock_rss), \
         patch('app.services.extraccion.manager.scrape_noticias', mock_scraper), \
         patch('app.services.extraccion.manager.obtener_noticias_browser', mock_browser):
        
        extraction_manager = NewsExtractorManager()
        resultados = extraction_manager.obtener_noticias()
        
        # Verificaciones:
        # 1. ¿Se llamó al RSS? (puede ser múltiples veces por múltiples fuentes)
        assert mock_rss.called, "RSS debería haberse intentado"
        
        # 2. ¿Se llamó al Scraper como fallback?
        assert mock_scraper.called, "Scraper debería haberse llamado como fallback"
        
        # 3. ¿El resultado contiene las noticias del scraper?
        assert len(resultados) > 0, "Debería haber noticias en el resultado"
        
        print("\n✅ TEST PASADO: Fallback RSS → Scraper funciona correctamente")
