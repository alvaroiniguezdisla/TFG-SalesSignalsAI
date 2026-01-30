import pytest
from unittest.mock import MagicMock, patch
from app.services.extraccion.manager import ExtractorManager
from app.services.extraccion import manager

@pytest.mark.asyncio
async def test_fallback_rss_to_scraper():
    """
    Test PROFESIONAL:
    Simula que el RSS falla (devuelve lista vacía) y verifica que
    el Manager llama automáticamente al Scraper como plan B.
    """
    
    # 1. Preparar el MOCK (el "doble" de nuestros servicios)
    # No queremos llamar a internet real, así que "parcheamos" las funciones
    
    # Simulamos que obtener_noticias_rss devuelve lista vacía []
    mock_rss = MagicMock(return_value=[])
    
    # Simulamos que el scraper SI funciona y devuelve 1 noticia dummy
    dummy_news = [{"titulo": "Noticia Test", "url": "http://test.com", "url_hash": "123"}]
    mock_scraper = MagicMock(return_value=dummy_news)
    
    # Aplicamos los parches (interceptamos las llamadas reales)
    with patch.object(manager, 'obtener_noticias_rss', mock_rss), \
         patch.object(manager, 'scrape_elpais_portada', mock_scraper):
        
        # 2. EJECUTAR (Action)
        extraction_manager = ExtractorManager()
        resultados = await extraction_manager.obtener_noticias()
        
        # 3. VERIFICAR (Assert)
        
        # A) ¿Se llamó al RSS? SI
        mock_rss.assert_called_once()
        
        # B) ¿Se llamó al Scraper? SI (porque el RSS falló)
        mock_scraper.assert_called_once()
        
        # C) ¿El resultado final es lo que devolvió el Scraper? SI
        assert len(resultados) == 1
        assert resultados[0]["titulo"] == "Noticia Test"
        print("\n✅ TEST PASADO: El sistema hizo fallback de RSS a Scraper correctamente.")
