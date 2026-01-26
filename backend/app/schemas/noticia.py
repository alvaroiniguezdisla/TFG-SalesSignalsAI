from pydantic import BaseModel
from typing import Optional, List

class Noticia(BaseModel):
    titulo: str
    url: str # Antes era 'link', normalizamos a 'url'
    url_hash: str
    fuente: str
    
    id: Optional[str] = None
    resumen: Optional[str] = None

    
    # Campos enriquecidos por IA
    relevancia_ia: int = 0
    resumen_comercial_ia: Optional[str] = None
    empresas_clave_ia: List[str] = []
    categoria_ia: Optional[str] = None
    categoria_producto_ia: Optional[str] = None
    
    published_at: Optional[str] = None
    scraped_at: Optional[str] = None
