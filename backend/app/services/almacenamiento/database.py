from supabase import create_client, Client
from app.core.config import settings
from datetime import datetime, timedelta
from app.core.deduplication import es_titulo_similar, fusionar_datos_noticia
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        #Leemos las credenciales del .env
        url: str =settings.SUPABASE_URL
        key: str = settings.SUPABASE_KEY
        self.client: Client = create_client(url, key)

    
    def insert_news_deduplicacion(self, news_list: list):
        """
        Version inteligente: antes de insertar datos en la DB 
        comparamos con las noticias existentes en la DB para evitar duplicados.
        Refactorizado para usar app.core.deduplication.
        """
        if not news_list:
            return 

        try:
            #1. Obtenemos las noticias de la DB de los 3 ultimos dias 
            fecha_3_dias_atras = (datetime.now() - timedelta(days=3)).isoformat()
            response = self.client.table("noticias")\
                .select("id, titulo, fuente, urls_extra, url, url_hash")\
                .gt("scraped_at", fecha_3_dias_atras)\
                .execute()

            noticias_db_3dias = response.data if response.data else []
            if noticias_db_3dias:
                logger.info(f"Se han encontrado {len(noticias_db_3dias)} noticias recientes en la DB")
            else:
                logger.info("No se han encontrado noticias recientes en la base de datos")

            nuevas_para_insertar = []
            hashes_procesados_lote = set()

            for nueva in news_list:
                # 0. Check Intra-Lote (Evitar duplicados dentro de la misma ejecucion)
                current_hash = nueva.get('url_hash')
                
                # Si no tiene hash o ya lo hemos procesado en este lote, saltamos
                if not current_hash or current_hash in hashes_procesados_lote:
                    continue
                
                # Lo marcamos como procesado
                hashes_procesados_lote.add(current_hash)

                es_duplicada_db = False
                
                # Comparar con noticias existentes en DB (noticias_db_3dias)
                for existente in noticias_db_3dias:
                    # Check 1: Mismo Hash (Exactamente la misma URL)
                    # 'existente' es la noticia de la DB, 'nueva' es la que intentamos insertar
                    mismo_hash = (existente.get('url_hash') == current_hash)
                    
                    # Check 2: Titulo Similar
                    titulo_similar = es_titulo_similar(nueva['titulo'], existente['titulo'])

                    if mismo_hash or titulo_similar:
                        es_duplicada_db = True
                        
                        # FUSIONAR DATOS
                        # Guardamos el estado original de la noticia en DB para detectar cambios
                        fuente_original = existente.get('fuente', '')
                        num_urls_original = len(existente.get('urls_extra') or [])
                        
                        # Esta funcion modifica 'existente' con los datos de 'nueva'
                        fusionar_datos_noticia(existente, nueva)
                        
                        # Detectar si ha habido cambios reales tras la fusion
                        fuente_nueva = existente.get('fuente', '')
                        num_urls_nueva = len(existente.get('urls_extra') or [])
                        
                        cambio_fuente = (fuente_nueva != fuente_original)
                        cambio_urls = (num_urls_nueva > num_urls_original)

                        if cambio_fuente or cambio_urls:
                            # Preparamos los datos a actualizar
                            payload = {}
                            if cambio_fuente:
                                payload['fuente'] = fuente_nueva
                            if cambio_urls:
                                payload['urls_extra'] = existente['urls_extra']
                                
                            # Actualizamos en DB
                            self.client.table("noticias").update(payload).eq("id", existente['id']).execute()
                            logger.info(f"    Fusión realizada en DB: {existente['titulo'][:30]}...")
                        
                        # Si encontramos duplicado, paramos de buscar en la DB para esta noticia
                        break 
                
                # Si recorrimos todas las existentes y ninguna coincidió, es NUEVA
                if not es_duplicada_db:
                    nuevas_para_insertar.append(nueva)
            
            # 3. Insertamos de golpe solo las nuevas
            if nuevas_para_insertar:
                self.client.table("noticias").insert(nuevas_para_insertar).execute()
            
            logger.info(f"Resultado: {len(nuevas_para_insertar)} Nuevas | {len(news_list) - len(nuevas_para_insertar)} Fusionadas")
            return True

        except Exception as e:
            logger.error(f"Error en insert_news_deduplicacion: {e}")
            return None
            
    def obtener_usuarios_preferencias(self):
        """Devuelve todos los perfiles de la base de datos."""
        try:
            response = self.client.table("profiles").select("*").execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error obteniendo usuarios de DB: {e}")
            return []
            
    def obtener_noticias_relevantes_recientes(self, horas=6, min_relevancia=40):
        """Devuelve noticias con relevancia mínima extraídas en las últimas X horas."""
        hace_x_horas = (datetime.utcnow() - timedelta(hours=horas)).isoformat()
        try:
            response = self.client.table("noticias")\
                .select("*")\
                .gt("scraped_at", hace_x_horas)\
                .gte("relevancia_ia", min_relevancia)\
                .order("relevancia_ia", desc=True)\
                .execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error obteniendo noticias recientes en DB: {e}")
            return []
        
# Instancia global para usar en el resto de la app
supabase_service = SupabaseService()
supabase = supabase_service.client
