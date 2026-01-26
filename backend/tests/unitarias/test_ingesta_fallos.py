# ----------------------------------------------------------------------------------
# TEST DE RESISTENCIA A FALLOS (JUEZ DE LINEA)
# Qué hace esto: Simula que la fuente RSS falla y comprueba que el sistema es listo
# y salta automáticamente al Scraper (Plan B) o al Navegador (Plan C).
# Para qué sirve: Para demostrar que el sistema es robusto y no se rompe si una web cae.
# ----------------------------------------------------------------------------------

import pytest 
from unittest.mock import MagicMock, patch
from app.services.extraccion.manager import NewsExtractorManager

# Test para ver que si falla el RSS salta al Scraper (que es el plan B)
def test_rss_falla_usa_scraper():
    
    # 1. Simulamos que el RSS falla (devuelve lista vacia)
    mock_rss = MagicMock(return_value=[])
    
    # 2. Simulamos que el Scraper SI funciona
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

    # Parcheamos las funciones reales para que no llame a internet de verdad
    with (patch("app.services.extraccion.manager.obtener_noticias_rss", mock_rss),
        patch("app.services.extraccion.manager.scrape_noticias", mock_scraper)):

        extractor = NewsExtractorManager()
        noticias = extractor.obtener_noticias()

        # Comprobamos que llamó al RSS
        assert mock_rss.call_count >= 1
        
        # Comprobamos que luego llamó al Scraper
        assert mock_scraper.call_count >= 1

        # Y que devolvió la noticia del scraper
        assert len(noticias) >= 1

# Test mas heavy: si falla RSS y Scraper, tira de Browser
def test_todo_falla_usa_browser():
    
    # Todos fallan menos el ultimo
    mock_rss = MagicMock(return_value=[])
    mock_scraper = MagicMock(return_value=[])

    mock_browser = MagicMock(return_value=[
        {
            "titulo": "Noticia de prueba browser",
            "url": "http://prueba.com",
            "fuente": "Browser",
        }
    ])

    with (patch("app.services.extraccion.manager.obtener_noticias_rss", mock_rss),
        patch("app.services.extraccion.manager.scrape_noticias", mock_scraper),
        patch("app.services.extraccion.manager.obtener_noticias_browser", mock_browser)):

        extractor = NewsExtractorManager()
        noticias = extractor.obtener_noticias()

        # Tienen que haberse ejecutado todos en orden
        assert mock_rss.call_count >= 1
        assert mock_scraper.call_count >= 1
        assert mock_browser.call_count >= 1

        # Al final recuperamos datos
        assert len(noticias) >= 1
