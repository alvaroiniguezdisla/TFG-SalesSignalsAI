# ----------------------------------------------------------------------------------
# TEST DE RESILIENCIA DEL SISTEMA DE EXTRACCION
#
# Objetivo: Verificar que el sistema de extraccion soporta fallos en las fuentes
# y activa automaticamente el siguiente metodo disponible (fallback en cascada).
#
# Que comprueba:
#   1. Si el RSS falla, el sistema salta al Scraper (Plan B).
#   2. Si RSS y Scraper fallan, el sistema salta al Browser (Plan C).
#   3. Si RSS funciona, NO se activan los metodos alternativos.
#   4. Si una fuente lanza excepcion, el sistema no se rompe.
# ----------------------------------------------------------------------------------

from unittest.mock import MagicMock, patch
from app.services.extraccion.manager import NewsExtractorManager


# Fuente de prueba con URL RSS y URL scraper/browser
FUENTE_TEST = [
    {"name": "Diario Test", "url": "http://rss.test.com/feed", "scraper_url": "http://test.com"}
]


def test_fallback_rss_a_scraper():
    """
    Si RSS no devuelve noticias, el manager activa el Scraper.
    Simula un escenario real: el feed RSS de una fuente esta roto o vacio.
    """
    noticia_scraper = [{
        "titulo": "Noticia de prueba",
        "url": "http://prueba.com",
        "fuente": "Scraper",
        "raw_content": "Contenido de prueba"
    }]

    mock_rss = MagicMock(return_value=[])
    mock_scraper = MagicMock(return_value=noticia_scraper)
    mock_browser = MagicMock(return_value=[])

    with patch("app.services.extraccion.manager.get_supabase_service") as mock_db, \
            patch("app.services.extraccion.manager.obtener_noticias_rss", mock_rss), \
            patch("app.services.extraccion.manager.scrape_noticias", mock_scraper), \
            patch("app.services.extraccion.manager.obtener_noticias_browser", mock_browser):

        mock_db.return_value.get_app_config.return_value = {"rss_sources": FUENTE_TEST}

        extractor = NewsExtractorManager()
        noticias = extractor.obtener_noticias()

        assert mock_rss.called, "Debio intentar RSS primero"
        assert mock_scraper.called, "Al fallar RSS, debio activar el Scraper"
        assert not mock_browser.called, "El Browser no debio activarse"
        assert len(noticias) == 1


def test_fallback_completo_rss_scraper_a_browser():
    """
    Si tanto RSS como Scraper fallan, el manager activa el Browser
    (Playwright) como ultimo recurso.
    """
    noticia_browser = [{
        "titulo": "Noticia de Browser",
        "url": "http://browser.com",
        "fuente": "Browser"
    }]

    mock_rss = MagicMock(return_value=[])
    mock_scraper = MagicMock(return_value=[])
    mock_browser = MagicMock(return_value=noticia_browser)

    with patch("app.services.extraccion.manager.get_supabase_service") as mock_db, \
            patch("app.services.extraccion.manager.obtener_noticias_rss", mock_rss), \
            patch("app.services.extraccion.manager.scrape_noticias", mock_scraper), \
            patch("app.services.extraccion.manager.obtener_noticias_browser", mock_browser):

        mock_db.return_value.get_app_config.return_value = {"rss_sources": FUENTE_TEST}

        extractor = NewsExtractorManager()
        noticias = extractor.obtener_noticias()

        assert mock_rss.called, "Debio intentar RSS"
        assert mock_scraper.called, "Debio intentar Scraper"
        assert mock_browser.called, "Al fallar todo, debio usar Browser"
        assert len(noticias) == 1


def test_rss_funciona_no_activa_fallback():
    """
    Si RSS funciona correctamente, el manager NO debe llamar
    ni al Scraper ni al Browser. Esto evita trabajo innecesario.
    """
    noticia_rss = [{
        "titulo": "Noticia RSS",
        "url": "http://rss.com",
        "fuente": "RSS"
    }]

    mock_rss = MagicMock(return_value=noticia_rss)
    mock_scraper = MagicMock(return_value=[])
    mock_browser = MagicMock(return_value=[])

    with patch("app.services.extraccion.manager.get_supabase_service") as mock_db, \
            patch("app.services.extraccion.manager.obtener_noticias_rss", mock_rss), \
            patch("app.services.extraccion.manager.scrape_noticias", mock_scraper), \
            patch("app.services.extraccion.manager.obtener_noticias_browser", mock_browser):

        mock_db.return_value.get_app_config.return_value = {"rss_sources": FUENTE_TEST}

        extractor = NewsExtractorManager()
        noticias = extractor.obtener_noticias()

        assert mock_rss.called, "RSS debio ser llamado"
        assert not mock_scraper.called, "El Scraper NO debio activarse"
        assert not mock_browser.called, "El Browser NO debio activarse"
        assert len(noticias) == 1


def test_excepcion_en_rss_no_rompe_sistema():
    """
    Si RSS lanza una excepcion (p.ej. timeout, DNS error), el manager
    la captura y salta al Scraper sin romperse.
    """
    noticia_scraper = [{
        "titulo": "Noticia Rescatada",
        "url": "http://rescate.com",
        "fuente": "Scraper"
    }]

    mock_rss = MagicMock(side_effect=Exception("Connection timeout"))
    mock_scraper = MagicMock(return_value=noticia_scraper)
    mock_browser = MagicMock(return_value=[])

    with patch("app.services.extraccion.manager.get_supabase_service") as mock_db, \
            patch("app.services.extraccion.manager.obtener_noticias_rss", mock_rss), \
            patch("app.services.extraccion.manager.scrape_noticias", mock_scraper), \
            patch("app.services.extraccion.manager.obtener_noticias_browser", mock_browser):

        mock_db.return_value.get_app_config.return_value = {"rss_sources": FUENTE_TEST}

        extractor = NewsExtractorManager()
        noticias = extractor.obtener_noticias()

        # El sistema no se rompio, obtuvo noticias del Scraper
        assert len(noticias) == 1
        assert noticias[0]["titulo"] == "Noticia Rescatada"


def test_fuente_caida_se_registra_sin_bloquear():
    """
    Si una fuente no devuelve noticias por ningun metodo, el manager
    debe registrar la incidencia y continuar sin lanzar excepcion.
    """
    mock_rss = MagicMock(return_value=[])
    mock_scraper = MagicMock(return_value=[])
    mock_browser = MagicMock(return_value=[])

    with patch("app.services.extraccion.manager.get_supabase_service") as mock_db, \
            patch("app.services.extraccion.manager.obtener_noticias_rss", mock_rss), \
            patch("app.services.extraccion.manager.scrape_noticias", mock_scraper), \
            patch("app.services.extraccion.manager.obtener_noticias_browser", mock_browser):

        mock_db.return_value.get_app_config.return_value = {"rss_sources": FUENTE_TEST}

        extractor = NewsExtractorManager()
        noticias = extractor.obtener_noticias()
        fuentes_caidas = extractor.get_ultimas_fuentes_caidas()

        assert noticias == []
        assert len(fuentes_caidas) == 1
        assert fuentes_caidas[0]["fuente"] == "Diario Test"
        assert len(fuentes_caidas[0]["errores"]) >= 1
