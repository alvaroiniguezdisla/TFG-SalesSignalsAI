from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SalesSignalsAI"
    
    # Esta variable buscará automáticamente "SCRAPER_TARGET_URL" en el .env
    SCRAPER_TARGET_URL: str = "https://elpais.com/"

    #URL del feed RSS
    RSS_TARGET_URL: str = "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"
    
    
    class Config:
        # Le decimos que si no encuentra la variable, mire en este archivo
        env_file = ".env"

# Instanciamos la configuración para poder importarla en otros sitios
settings = Settings()