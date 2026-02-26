from fastapi import APIRouter, HTTPException, Depends
from app.schemas.admin import AppConfig
from app.services.almacenamiento.database import get_supabase_service, SupabaseService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/config", response_model=AppConfig)
def get_admin_config(db: SupabaseService = Depends(get_supabase_service)):
    """Obtiene la configuración global (Dynamic Config) para el Dashboard Admin."""
    try:
        config_data = db.get_app_config()
        if not config_data:
            # Fallback en caso de que la tabla esté vacía (no debería ocurrir en SaaS estable)
            raise HTTPException(status_code=404, detail="Configuración no encontrada en base de datos.")
        
        return config_data
    except Exception as e:
        logger.error(f"Error en GET /config: {e}")
        raise HTTPException(status_code=500, detail="Error interno al obtener configuración.")

@router.put("/config", response_model=AppConfig)
def update_admin_config(new_config: AppConfig, db: SupabaseService = Depends(get_supabase_service)):
    """Sobreescribe la configuración global desde el Dashboard Admin."""
    try:
        # Pydantic valida new_config. Lo pasamos a dict para Supabase.
        # Excluimos valores por defecto que no apliquen o metadatos extras.
        config_dict = new_config.model_dump()
        
        updated_data = db.update_app_config(config_dict)
        if not updated_data:
            raise HTTPException(status_code=400, detail="No se pudo actualizar la configuración en BD.")
            
        logger.info("[ADMIN] Configuración global actualizada con éxito.")
        return updated_data
    except Exception as e:
        logger.error(f"Error en PUT /config: {e}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar configuración.")
