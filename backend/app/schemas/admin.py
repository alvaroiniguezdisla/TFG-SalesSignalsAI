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

class UserRoleUpdate(BaseModel):
    role: str

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "user"

class AdminMetricsResponse(BaseModel):
    total_users: int
    active_users_30d: int
    total_news: int
    news_7d: int
    total_feedbacks: int
    likes_count: int
    dislikes_count: int
    active_sources: int
