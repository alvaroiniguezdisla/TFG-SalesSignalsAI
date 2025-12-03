from pydantic import BaseModel

class Noticia(BaseModel):
    titulo: str
    link: str
