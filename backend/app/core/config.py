import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SalesSignalsAI"
    
    # Esta variable buscará automáticamente "SCRAPER_TARGET_URL" en el .env
    SCRAPER_TARGET_URL: str = "https://cincodias.elpais.com/companias/"
    
    #URL del feed RSS
    RSS_SOURCES: list[dict] = [
        # Fuente 1: Cinco Días
        {
            "name": "Cinco Días (Compañías)",
            "url": "https://feeds.elpais.com/mrss-s/list/ep/site/cincodias.elpais.com/section/companias", # RSS (XML)
            "scraper_url": "https://cincodias.elpais.com/companias/", # FALLBACK (HTML)
            "type": "rss"
        },
        # Fuente 2: El Economista 
        {
            "name": "El Economista (Mercados)",
            "url": "https://www.eleconomista.es/rss/rss-mercados.php", 
            "scraper_url": "https://www.eleconomista.es/empresas-finanzas/", # HTML SOLICITADO
            "type": "rss"
        }
    ]
    #economismta, bolsa española


    # Supabase Credentials
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # Email Notifications (Gmail SMTP)
    GMAIL_USER: str = ""
    GMAIL_APP_PASSWORD: str = ""
    
    # Configuración de envíos
    MAX_EMAILS_POR_EJECUCION: int = 50
    DELAY_ENTRE_EMAILS: int = 1
    
    # Configuración Deduplicación
    UMBRAL_SIMILITUD_TITULOS: float = 0.82
    
    # LLM Settings
    OLLAMA_MODEL: str = "llama3.1"
    
    class Config:
        # Le decimos que busque el .env relativo a este archivo (backend/app/core/../../.env)
        # Esto asegura que lo encuentre aunque lancemos el script desde otra carpeta
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")

# Instanciamos la configuración para poder importarla en otros sitios
settings = Settings()