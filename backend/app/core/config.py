import os
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SalesSignalsAI"

    # Supabase Credentials (requeridos para conectar con la config dinámica)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    


    # Microsoft Graph API Notifications
    GRAPH_TENANT_ID: str = ""
    GRAPH_CLIENT_ID: str = ""
    GRAPH_SCOPES: str = "User.Read Chat.ReadWrite ChatMessage.Send"
    TEAMS_TARGET_USER_EMAIL: str = ""
    
    # CORS Origins Permitidos
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Le decimos que busque el .env relativo a este archivo (backend/app/core/../../.env)
    # Esto asegura que lo encuentre aunque lancemos el script desde otra carpeta.
    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            ".env",
        )
    )

# Instanciamos la configuración para poder importarla en otros sitios
settings = Settings()
