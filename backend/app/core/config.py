import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SalesSignalsAI"

    # Supabase Credentials (requeridos para conectar con la config dinámica)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # Email Notifications (Gmail SMTP)
    GMAIL_USER: str = ""
    GMAIL_APP_PASSWORD: str = ""
    
    # CORS Origins Permitidos
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    class Config:
        # Le decimos que busque el .env relativo a este archivo (backend/app/core/../../.env)
        # Esto asegura que lo encuentre aunque lancemos el script desde otra carpeta
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")

# Instanciamos la configuración para poder importarla en otros sitios
settings = Settings()