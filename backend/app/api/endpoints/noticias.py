from fastapi import APIRouter, Query
from typing import List
from app.services.almacenamiento.database import supabase
from app.schemas.noticia import Noticia
from app.services.orquestacion.pipeline import NewsPipeline

router = APIRouter()

@router.get("/noticias", response_model=List[Noticia])
def get_noticias():
    """
    Obtiene las noticias YA procesadas de la Base de Datos.
    Esta es la ruta que consumirá el Frontend.
    """
    # Consultamos Supabase, ordenamos por fecha (descendente)
    response = supabase.table("noticias").select("*").order("scraped_at", desc=True).execute()
    
    return response.data

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
        return {"status":"error", "message":str(e)}