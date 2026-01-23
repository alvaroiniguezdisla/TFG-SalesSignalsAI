from .scraper import scrape_noticias
from .rss import obtener_noticias_rss
from .browser import obtener_noticias_browser
from .manager import extractor

#Instancia global para usar en pipeline

__all__= ["scrape_elpais_portada", "obtener_noticias_rss", "obtener_noticias_browser", "extractor"]