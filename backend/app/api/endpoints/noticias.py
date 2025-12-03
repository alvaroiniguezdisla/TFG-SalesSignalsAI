from fastapi import APIRouter
from typing import List
from app.services.scraper import obtener_noticias
from app.schemas.noticia import Noticia

router = APIRouter()

@router.get("/noticias", response_model=List[Noticia])
def get_noticias():
    """
    Obtiene las últimas noticias de la portada de El País.
    """
    return obtener_noticias()
