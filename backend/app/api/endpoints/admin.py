from fastapi import APIRouter, HTTPException, Depends
from app.schemas.admin import AppConfig, UserCreate
from app.services.almacenamiento.database import get_supabase_service, SupabaseService
from app.services.inteligencia.llm_clasificacion_noticias import PROMPT_DEFAULT
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
            
        config_data['ai_prompt_default'] = PROMPT_DEFAULT.strip()
        current_prompt = config_data.get('ai_prompt') or ""
        if not current_prompt.strip():
            config_data['ai_prompt'] = config_data['ai_prompt_default']
        
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
        config_dict.pop("ai_prompt_default", None)
        
        updated_data = db.update_app_config(config_dict)
        if not updated_data:
            raise HTTPException(status_code=400, detail="No se pudo actualizar la configuración en BD.")
            
        updated_data['ai_prompt_default'] = PROMPT_DEFAULT.strip()
        logger.info("Configuración global actualizada con éxito.")
        return updated_data
    except Exception as e:
        logger.error(f"Error en PUT /config: {e}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar configuración.")

# --- PHASE 3: USERS & METRICS ENDPOINTS ---

@router.get("/users")
def get_all_users(db: SupabaseService = Depends(get_supabase_service)):
    """Devuelve la lista completa de perfiles de la DB (para Panel Admin)."""
    try:
        users = db.obtener_usuarios_preferencias()
        return users
    except Exception as e:
        logger.error(f"Error en GET /users: {e}")
        raise HTTPException(status_code=500, detail="Error interno al obtener usuarios.")

@router.put("/users/{user_id}/role")
def change_user_role(user_id: str, payload: dict, db: SupabaseService = Depends(get_supabase_service)):
    """Cambia el rol (user/admin) a un usuario concreto en Supabase."""
    new_role = payload.get("role")
    if not new_role or new_role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Rol inválido. Debe ser 'user' o 'admin'.")
        
    try:
        updated_profile = db.update_user_role(user_id, new_role)
        if not updated_profile:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        
        logger.info(f"Usuario {user_id} actualizado a rol {new_role}")
        return {"message": "Rol actualizado con éxito", "profile": updated_profile}
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error en PUT /users/{user_id}/role: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar rol de usuario.")

@router.get("/metrics")
def get_system_metrics(db: SupabaseService = Depends(get_supabase_service)):
    """Obtiene datos estadísticos de alto nivel (KPIs) para visualizar en tarjetas Admin."""
    try:
        metrics = db.get_admin_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error en GET /metrics: {e}")
        raise HTTPException(status_code=500, detail="Error al calcular métricas del sistema.")

@router.post("/users")
def create_new_user(user: UserCreate, db: SupabaseService = Depends(get_supabase_service)):
    """Crea un perfil de usuario directamente desde el panel de administrador usando Service Role Key."""
    try:
        new_user = db.create_user(email=user.email, password=user.password, role=user.role)
        logger.info(f"Usuario creado con éxito: {user.email}")
        return {"message": "Usuario creado correctamente", "user": new_user}
    except Exception as e:
        logger.error(f"Error en POST /users: {e}")
        # Simplificamos el error al dashboard
        error_str = str(e)
        if "User already registered" in error_str or "already exists" in error_str:
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")
        raise HTTPException(status_code=500, detail=f"Error creando usuario: {error_str}")

@router.delete("/users/{user_id}")
def delete_existing_user(user_id: str, db: SupabaseService = Depends(get_supabase_service)):
    """Elimina permanentemente una cuenta de usuario."""
    try:
        success = db.delete_user(user_id)
        if success:
            logger.info(f"Usuario eliminado con éxito: {user_id}")
            return {"message": "Usuario eliminado permanentemente"}
        raise HTTPException(status_code=400, detail="No se pudo eliminar el usuario.")
    except Exception as e:
        logger.error(f"Error en DELETE /users/{user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error al intentar eliminar el usuario.")
