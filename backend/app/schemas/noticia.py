from pydantic import BaseModel
from typing import Optional

class Noticia(BaseModel):
    titulo: str
    link: str
    resumen: Optional[str] = None
