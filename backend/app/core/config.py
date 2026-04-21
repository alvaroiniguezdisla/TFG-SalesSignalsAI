import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SalesSignalsAI"

    # Credenciales de Supabase necesarias para cargar la configuracion dinamica.
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Configuracion opcional para notificaciones por Teams.
    GRAPH_TENANT_ID: str = ""
    GRAPH_CLIENT_ID: str = ""
    GRAPH_SCOPES: str = "User.Read Chat.ReadWrite ChatMessage.Send"
    TEAMS_TARGET_USER_EMAIL: str = ""

    # Origenes permitidos para el frontend en desarrollo.
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # El .env se resuelve desde la raiz del backend para que funcione igual
    # aunque la app se arranque desde carpetas distintas.
    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            ".env",
        )
    )

# Instancia compartida para importar la configuracion en el resto del backend.
settings = Settings()
