import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SalesSignalsAI"
    
    # Esta variable buscará automáticamente "SCRAPER_TARGET_URL" en el .env
    SCRAPER_TARGET_URL: str = "https://elpais.com/"

    #URL del feed RSS
    RSS_TARGET_URL: str = "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"

    # Supabase Credentials
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    class Config:
        # Le decimos que busque el .env relativo a este archivo (backend/app/core/../../.env)
        # Esto asegura que lo encuentre aunque lancemos el script desde otra carpeta
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")

# Instanciamos la configuración para poder importarla en otros sitios
settings = Settings()