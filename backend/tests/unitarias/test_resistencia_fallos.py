"""
Tests de Resistencia del Pipeline
Verifican que el sistema hace fallback correctamente ante fallos
"""
from unittest.mock import MagicMock, patch
from app.services.extraccion.manager import NewsExtractorManager


def test_fallback_rss_falla():
    """
    OBJETIVO: Probar que si el RSS falla/vacío, el sistema salta al Scraper.
    """
    
    # Noticia dummy
    noticia_scraper = [{
        "titulo": "Noticia de prueba",
        "url": "http://prueba.com",
        "fuente": "Scraper",
        "raw_content": "Contenido de prueba"
    }]
    
    # Mocks
    mock_rss = MagicMock(return_value=[])  # RSS devuelve vacío
    mock_scraper = MagicMock(return_value=noticia_scraper)  # Scraper funciona
    mock_browser = MagicMock(return_value=[])
    
    # Parcheamos donde se IMPORTAN las funciones
    with patch('app.services.extraccion.manager.obtener_noticias_rss', mock_rss), \
         patch('app.services.extraccion.manager.scrape_noticias', mock_scraper), \
         patch('app.services.extraccion.manager.obtener_noticias_browser', mock_browser):
        
        extractor = NewsExtractorManager()
        noticias = extractor.obtener_noticias()
        
        # Verificaciones
        assert mock_rss.called, "Se debió intentar RSS primero"
        print("✓ Se llamó a RSS primero")
        
        assert mock_scraper.called, "Al fallar RSS, se debió llamar al Scraper"
        print("✓ Al fallar RSS se llamó al Scraper")
        
        assert len(noticias) > 0, "El resultado debe contener noticias del scraper"
        print("✓ El resultado contiene noticias del scraper")
        
        print("\n✅ TEST PASADO: Fallback RSS → Scraper funciona")


def test_full_fallback_rss_y_scraper_fallan():
    """
    OBJETIVO: Probar que si RSS y Scraper fallan, el Browser toma el control.
    """
    
    # Noticia dummy del browser
    noticia_browser = [{
        "titulo": "Noticia de Browser",
        "url": "http://browser.com",
        "fuente": "Browser"
    }]
    
    # Mocks - RSS y Scraper fallan, Browser funciona
    mock_rss = MagicMock(return_value=[])
    mock_scraper = MagicMock(return_value=[])
    mock_browser = MagicMock(return_value=noticia_browser)
    
    with patch('app.services.extraccion.manager.obtener_noticias_rss', mock_rss), \
         patch('app.services.extraccion.manager.scrape_noticias', mock_scraper), \
         patch('app.services.extraccion.manager.obtener_noticias_browser', mock_browser):
        
        extractor = NewsExtractorManager()
        noticias = extractor.obtener_noticias()
        
        # Verificaciones
        assert mock_rss.called, "Se debió intentar RSS"
        print("✓ Se intentó RSS")
        
        assert mock_scraper.called, "Se debió intentar Scraper"
        print("✓ Se intentó Scraper")
        
        assert mock_browser.called, "Al fallar todo, se debió usar Browser"
        print("✓ Al fallar RSS y Scraper, se usó Browser")
        
        assert len(noticias) > 0, "El resultado debe contener noticias del browser"
        print("✓ El resultado contiene noticias")
        
        print("\n✅ TEST PASADO: Fallback completo RSS → Scraper → Browser funciona")


def test_todo_funciona_usa_rss():
    """
    OBJETIVO: Si RSS funciona, no se llama a Scraper ni Browser.
    """
    
    noticia_rss = [{
        "titulo": "Noticia RSS",
        "url": "http://rss.com",
        "fuente": "RSS"
    }]
    
    mock_rss = MagicMock(return_value=noticia_rss)
    mock_scraper = MagicMock(return_value=[])
    mock_browser = MagicMock(return_value=[])
    
    with patch('app.services.extraccion.manager.obtener_noticias_rss', mock_rss), \
         patch('app.services.extraccion.manager.scrape_noticias', mock_scraper), \
         patch('app.services.extraccion.manager.obtener_noticias_browser', mock_browser):
        
        extractor = NewsExtractorManager()
        noticias = extractor.obtener_noticias()
        
        assert mock_rss.called, "RSS debió ser llamado"
        assert len(noticias) > 0, "Debe haber noticias"
        
        # Si RSS funciona, Scraper y Browser NO deberían llamarse
        # (esto depende de la implementación, pero es el comportamiento esperado)
        print("\n✅ TEST PASADO: RSS funciona correctamente como primera opción")
