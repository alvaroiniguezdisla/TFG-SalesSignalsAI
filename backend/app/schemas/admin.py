from pydantic import BaseModel
from typing import List

class RssSource(BaseModel):
    name: str
    url: str
    scraper_url: str
    type: str

class AppConfig(BaseModel):
    umbral_similitud: float
    max_emails_ejecucion: int
    delay_entre_emails: int
    ollama_model: str
    ai_prompt: str = ""
    rss_sources: List[RssSource]
