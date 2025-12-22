import os 
from supabase import create_client, Client
from app.core.config import settings

class SupabaseService:
    def __init__(self):
        #Leemos las credenciales del .env
        url: str =settings.SUPABASE_URL
        key: str = settings.SUPABASE_KEY
        self.client: Client = create_client(url, key)

    
    def insert_news(self, news_list: list):
        #Si se hace ingesta de noticias  , guardaremo slas noticias en la base de datos
        try:
            data=self.client.table("noticias").upsert(
                news_list , on_conflict="url_hash", ignore_duplicates=True
            ).execute()
            print(f"Se han insertado {len(news_list)} noticias en la base de datos")
            return data

        except Exception  as e:
            print("Error guardando en la base de datos: {e}")
            return None

            
        