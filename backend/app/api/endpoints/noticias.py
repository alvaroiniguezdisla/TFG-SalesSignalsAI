import logging
from fastapi import APIRouter
from typing import List
from app.services.almacenamiento.database import get_supabase_client
from app.schemas.noticia import Noticia
from app.services.orquestacion.pipeline import NewsPipeline
from fastapi.exceptions import HTTPException

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/noticias", response_model=List[Noticia])
def get_noticias():
    """
    Obtiene las noticias YA procesadas de la Base de Datos.
    Esta es la ruta que consumirá el Frontend.
    """
    # Consultamos Supabase, ordenamos por fecha (descendente)
    response = get_supabase_client().table("noticias").select("*").order("scraped_at", desc=True).execute()
    
    return response.data

@router.get("/noticias/categorias")
def get_categories():
    """
    Devuelve las categorías oficiales del sistema (definidas en el Backend).
    Esto asegura que el Frontend siempre tenga los mismos valores que la IA.
    """
    # Importamos aquí mismo para evitar dependencias  
    from app.services.inteligencia.llm_clasificacion_noticias import ProductCategory, SignalCategory

    return {
        "signals": [c.value for c in SignalCategory],
        "products": [c.value for c in ProductCategory]
    }

@router.post("/refrescar")
def refrescar_noticias():
    """
    Endpoint manual para forzar la ejecucion del Pipeline(Scraping + IA + DB).
    """
    try:
        pipeline = NewsPipeline()
        pipeline.ejecutar()
        return {"status":"ok", "message":"Pipeline ejecutado. Nuevas noticias disponibles."}

    except Exception as e:
        logger.error(f"Error en POST /refrescar: {e}")
        raise HTTPException(status_code=500, detail=f"Error ejecutando el pipeline: {e}")


@router.get("/noticias/{url_hash}", response_model= Noticia)
def get_noticia_detalle(url_hash: str):
    """
    Obtiene una noticia por su url_hash (que es el id de la noticia en Supabase).
    """

    response = get_supabase_client().table("noticias").select("*").eq("url_hash", url_hash).execute()

    # Validar si existe
    if not response.data:
        raise HTTPException(status_code=404, detail="Noticia no encontrada")
    
    return response.data[0]

    
