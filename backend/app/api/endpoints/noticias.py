from fastapi import APIRouter, Query
from typing import List
from app.services.almacenamiento.database import supabase
from app.schemas.noticia import Noticia

router = APIRouter()

@router.get("/noticias", response_model=List[Noticia])
def get_noticias():
    """
    Obtiene las noticias YA procesadas de la Base de Datos.
    Esta es la ruta que consumirá el Frontend.
    """
    # Consultamos Supabase, ordenamos por fecha (descendente)
    response = supabase.table("noticias_procesadas").select("*").order("scraped_at", desc=True).execute()
    
    return response.data
