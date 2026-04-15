from .scraper import scrape_noticias
from .rss import obtener_noticias_rss
from .browser import obtener_noticias_browser
from .manager import get_extractor_manager

__all__ = [
    "scrape_noticias",
    "obtener_noticias_rss",
    "obtener_noticias_browser",
    "get_extractor_manager",
]
