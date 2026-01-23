import pytest 
from unittest.mock  import MagicMock , patch
from app.services.extraccion import manager
from app.services.extraccion.manager import NewsExtractorManager

def test_fallback_rss_falla():
    """
    OBJETIVO: Probar que si el RSS falla, el sistema salta AUTOMATICAMENTE al Scraper.Vamos
    a usar 'Mocks' para no hacer llamadas sobre los servidores web de la web real.
    """
    
    #1. Preparamos un Mock para simular que RSS falla
    #Simulamos que devuleve una lista vacia
    mock_rss = MagicMock(return_value=[])
    
    #2. Preparamos un Mock para simular que Scraper funciona
    mock_scraper = MagicMock(return_value=[
        {
            "titulo": "Noticia de prueba",
            "url": "http://prueba.com",
            "fuente": "Scraper",
            "raw_content": "Contenido de prueba",
            "resumen": "Resumen de prueba",
            "scraped_at": "2026-01-01T00:00:00"
        }
    ])

    #3. Aplicamos los Parches a las funciones reales
    with (patch.object(manager, "obtener_noticias_rss", mock_rss),
        patch.object(manager, "scrape_elpais_portada", mock_scraper)):

        #4. Ejecutamos el Manager
        extractor =NewsExtractorManager()
        noticias = extractor.obtener_noticias()

        #5.Verificaciones

        #A)Se llamo a RSS primero?
        mock_rss.assert_called_once()
        print("Se llamo a RSS primero")
        
        #B)Se llamo al scraper despues?? 
        mock_scraper.assert_called_once()
        print("Al fallar RSS se llamo al scraper despues")

        #C)El resultado es la noticia obtenida por el scraper?
        assert noticias == mock_scraper.return_value
        print("El resultado es la noticia obtenida por el scraper")


def test_full_fallback_rss_y_scraper_fallan():
    """
    OBJETIVO: Probar que si el RSS y el Scraper fallan, el sistema salta AUTOMATICAMENTE al Browser.Vamos
    a usar 'Mocks' para no hacer llamadas sobre los servidores web de la web real.
    """
    
    #1. Preparamos un Mock para simular que RSS falla
    #Simulamos que devuleve una lista vacia
    mock_rss = MagicMock(return_value=[])
    
    #2. Preparamos un Mock para simular que Scraper funciona
    mock_scraper = MagicMock(return_value=[])

    #3. Preparamos un Mock para simular que Browser funciona
    mock_browser = MagicMock(return_value=[
        {
            "titulo": "Noticia de prueba",
            "url": "http://prueba.com",
            "fuente": "Browser",
            "raw_content": "Contenido de prueba",
            "resumen": "Resumen de prueba",
            "scraped_at": "2026-01-01T00:00:00"
        }
    ])

    #4. Aplicamos los Parches a las funciones reales
    
    with (patch.object(manager, "obtener_noticias_rss", mock_rss),
         patch.object(manager, "scrape_elpais_portada", mock_scraper),
         patch.object(manager, "obtener_noticias_browser", mock_browser)):

        #5. Ejecutamos el Manager
        extractor =NewsExtractorManager()
        noticias = extractor.obtener_noticias()

        #6.Verificaciones

        #A)Se llamo a RSS primero?
        mock_rss.assert_called_once()
        print("Se llamo a RSS primero")
        
        #B)Se llamo al scraper despues?? 
        mock_scraper.assert_called_once()
        print("Al fallar RSS se llamo al scraper despues")

        #C)Se llamo al browser despues?? 
        mock_browser.assert_called_once()
        print("Al fallar RSS y Scraper se llamo al browser despues")

        #D)El resultado es la noticia obtenida por el browser?
        assert noticias == mock_browser.return_value
        print("El resultado es la noticia obtenida por el browser")



