import os 
from supabase import create_client, Client
from app.core.config import settings
from datetime import datetime, timedelta
from app.core.deduplication import es_titulo_similar, fusionar_datos_noticia

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
                print(f"Se han encontrado {len(noticias_db_3dias)} noticias recientes en la DB")
            else:
                print("No se han encontrado noticias recientes en la base de datos")

            nuevas_para_insertar = []
            hashes_procesados_lote = set()

            for nueva in news_list:
                # 0. Check Intra-Lote (Evitar duplicados dentro de la misma ejecucion)
                current_hash = nueva.get('url_hash')
                if current_hash and current_hash in hashes_procesados_lote:
                    print(f"    [SKIP] Noticia duplicada dentro del lote: {nueva['titulo'][:30]}...")
                    continue
                
                if current_hash:
                    hashes_procesados_lote.add(current_hash)

                es_duplicada_db = False
                
                # las comparamos con las de la base de datos
                for existente in noticias_db_3dias:
                    # Usamos la lógica compartida de app.core.deduplication
                    # Check 1: Mismo Hash (Exactamente la misma URL)
                    mismo_hash = (current_hash and existente.get('url_hash') and current_hash == existente['url_hash'])
                    
                    # Check 2: Titulo Similar
                    titulo_similar = es_titulo_similar(nueva['titulo'], existente['titulo'])

                    if mismo_hash or titulo_similar:
                        es_duplicada_db = True
                        
                        # Usamos la lógica de fusión compartida
                        # Guardamos estado previo para comparar cambios
                        fuente_previa = existente.get('fuente', '')
                        urls_previas_len = len(existente.get('urls_extra') or [])
                        
                        # Fusionamos en memoria (modifica 'existente')
                        cambios = fusionar_datos_noticia(existente, nueva)
                        
                        if cambios:
                            # Preparamos payload SOLO con lo que ha cambiado para el UPDATE
                            payload = {}
                            if existente.get('fuente') != fuente_previa:
                                payload['fuente'] = existente['fuente']
                            
                            urls_nuevas_len = len(existente.get('urls_extra') or [])
                            if urls_nuevas_len > urls_previas_len:
                                payload['urls_extra'] = existente['urls_extra']
                                
                            if payload:
                                self.client.table("noticias").update(payload).eq("id", existente['id']).execute()
                                print(f"    Fusión en DB: {existente['titulo'][:30]}...")
                        
                        break # Ya la encontramos, pasamos a la siguiente
                
                # Si no se parecía a ninguna, es NUEVA de verdad
                if not es_duplicada_db:
                    nuevas_para_insertar.append(nueva)
            
            # 3. Insertamos de golpe solo las nuevas
            if nuevas_para_insertar:
                self.client.table("noticias").insert(nuevas_para_insertar).execute()
            
            print(f" Resultado: {len(nuevas_para_insertar)} Nuevas | {len(news_list) - len(nuevas_para_insertar)} Fusionadas")
            return True

        except Exception as e:
            print(f"Error en insert_news_deduplicacion: {e}")
            return None
        
# Instancia global para usar en el resto de la app
supabase_service = SupabaseService()
supabase = supabase_service.client
