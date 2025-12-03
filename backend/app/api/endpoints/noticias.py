from fastapi import APIRouter, Query
from typing import List
from app.services.scraper import obtener_noticias
from app.services.rss import obtener_noticias_rss 
from app.schemas.noticia import Noticia

router = APIRouter()

@router.get("/noticias", response_model=List[Noticia])
def get_noticias(metodo: str = Query("html" , description="Metodo de obtención: 'html' o 'rss'")):
    """
    Obtiene las últimas noticias de la portada de El País.
    Permite elegir entre scrapping HTML o RSS
    """

    if metodo == "rss":
        return obtener_noticias_rss()
    return obtener_noticias()
