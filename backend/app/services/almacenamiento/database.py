from supabase import create_client, Client
from app.core.config import settings
from datetime import datetime, timedelta
from app.core.deduplication import es_titulo_similar, fusionar_datos_noticia
import logging
import time

logger = logging.getLogger(__name__)

class SupabaseService:

    # ------------------------------------------------------------------ #
    #                         INICIALIZACION                              #
    # ------------------------------------------------------------------ #

    def __init__(self):
        #Leemos las credenciales del .env
        url: str =settings.SUPABASE_URL
        key: str = settings.SUPABASE_KEY
        service_role_key: str = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
        self.client: Client = create_client(url, key)
        
        # Cliente Admin con privilegios elevados (para crear/borrar usuarios de auth)
        if service_role_key:
            self.admin_client: Client = create_client(url, service_role_key)
        else:
            self.admin_client = None

    # ------------------------------------------------------------------ #
    #                NOTICIAS: Insercion y Consulta                       #
    # ------------------------------------------------------------------ #

    def insert_news_deduplicacion(self, news_list: list):
        """
        Version inteligente: antes de insertar datos en la DB 
        comparamos con las noticias existentes en la DB para evitar duplicados.
        Refactorizado para usar app.core.deduplication.
        """
        if not news_list:
            return 
            
        try:
            # Obtenemos dinámicamente el umbral configurado por el SaaS admin
            app_config = self.get_app_config()
            umbral_similitud = app_config.get("umbral_similitud", 0.85)
            
            # 1. Obtenemos las noticias de la DB de los 3 ultimos dias para la busqueda difusa
            fecha_3_dias_atras = (datetime.now() - timedelta(days=3)).isoformat()
            response = self.client.table("noticias")\
                .select("id, titulo, fuente, urls_extra, url, url_hash")\
                .gt("scraped_at", fecha_3_dias_atras)\
                .execute()

            # 1.5. Y TAMBIEN forzamos la obtención de cualquier noticia (sin importar si tiene 5 años)
            # que coincida exactamente con los hashes de las noticias que vienen ahora, para que NO se escapen.
            hashes_entrada = [n.get('url_hash') for n in news_list if n.get('url_hash')]
            res_hashes = None
            if hashes_entrada:
                res_hashes = self.client.table("noticias")\
                    .select("id, titulo, fuente, urls_extra, url, url_hash")\
                    .in_("url_hash", hashes_entrada)\
                    .execute()

            # Unificamos ambos arrays de la base de datos sin duplicados
            dic_noticias = {n['url_hash']: n for n in (response.data or [])}
            if res_hashes and res_hashes.data:
                for n in res_hashes.data:
                    dic_noticias[n['url_hash']] = n
                    
            noticias_db_3dias = list(dic_noticias.values())

            if noticias_db_3dias:
                logger.info(f"Se han encontrado {len(noticias_db_3dias)} noticias en la DB para deduplicar")
            else:
                logger.info("No se han encontrado noticias en la base de datos")

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
                    titulo_similar = es_titulo_similar(nueva['titulo'], existente['titulo'], umbral_similitud)

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
                # Limpiar IDs si son None para dejar que Supabase los genere
                for n in nuevas_para_insertar:
                    if 'id' in n and n['id'] is None:
                        del n['id']
                        
                self.client.table("noticias").insert(nuevas_para_insertar).execute()
            
            logger.info(f"Resultado: {len(nuevas_para_insertar)} Nuevas procesadas | {len(news_list) - len(nuevas_para_insertar)} Fusionadas/Descartadas")
            return True

        except Exception as e:
            logger.error(f"Error en insert_news_deduplicacion: {e}")
            return None
            
    # ------------------------------------------------------------------ #
    #                USUARIOS: Perfiles y Roles                          #
    # ------------------------------------------------------------------ #

    def obtener_usuarios_preferencias(self):
        """Devuelve todos los perfiles de la base de datos."""
        try:
            # Seleccionamos también el role para el Admin Dashboard
            response = self.client.table("profiles").select("*").execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error obteniendo usuarios de DB: {e}")
            return []

    def create_user(self, email: str, password: str, role: str) -> dict:
        """
        Registra un nuevo usuario en la plataforma utilizando la API de administración de Supabase Auth.
        Tras la creación exitosa, se actualiza el perfil público generado automáticamente para 
        asignar el rol especificado.

        Args:
            email (str): Correo electrónico del nuevo usuario.
            password (str): Contraseña temporal inicial.
            role (str): Rol asignado ('user' o 'admin').
            
        Returns:
            dict: Diccionario que contiene el ID, email y rol del usuario recién creado.
            
        Raises:
            Exception: Si la configuración `service_role_key` no está disponible o falla la inserción.
        """
        if not self.admin_client:
            raise Exception("No hay service_role_key configurada en el backend.")
        
        try:
            # 1. Crear el usuario en auth.users (email_confirm: True auto-valida el correo)
            new_user = self.admin_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True
            })
            
            user_id = new_user.user.id
            
            # 2. Actualizar el rol en la tabla profiles (que fue creada automáticamente por el trigger)
            # Damos un pequeño delay/reintento para asegurar que el trigger de BD ha finalizado
            time.sleep(1)
            self.admin_client.table("profiles").update({
                "role": role, 
                "first_name": email.split('@')[0]
            }).eq("id", user_id).execute()
            
            return {"id": user_id, "email": email, "role": role}
        except Exception as e:
            logger.error(f"Error creando usuario {email}: {e}")
            raise e

    def delete_user(self, user_id: str) -> bool:
        """
        Elimina permanentemente una identidad de usuario del sistema de autenticación primario.
        Esta acción desencadenará políticas de borrado en cascada (CASCADE) en la base de datos
        para limpiar registros huérfanos asociados al usuario.

        Args:
            user_id (str): UUID del usuario a eliminar.
            
        Returns:
            bool: True si la eliminación fue exitosa.
        """
        if not self.admin_client:
            raise Exception("No hay service_role_key configurada en el backend.")
            
        try:
            self.admin_client.auth.admin.delete_user(user_id)
            return True
        except Exception as e:
            logger.error(f"Error eliminando usuario {user_id}: {e}")
            raise e

    def update_user_role(self, user_id: str, new_role: str) -> dict:
        """
        Actualiza el nivel de privilegios (rol) de un usuario existente.
        
        Args:
            user_id (str): UUID del perfil a actualizar.
            new_role (str): Nuevo rol a asignar. Debe ser 'user' o 'admin'.
        
        Returns:
            dict: Objeto del perfil actualizado.
            
        Raises:
            ValueError: Si el rol proporcionado no está dentro de la lista permitida.
        """
        if new_role not in ["user", "admin"]:
            raise ValueError("Rol no válido")
            
        try:
            response = self.client.table("profiles").update({"role": new_role}).eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error actualizando rol del usuario {user_id}: {e}")
            raise e

    # ------------------------------------------------------------------ #
    #                METRICAS: KPIs del Admin Dashboard                   #
    # ------------------------------------------------------------------ #

    def get_admin_metrics(self) -> dict:
        """Recopila KPIs clave estadísticos sobre el uso de la plataforma."""
        metrics = {
            "total_users": 0,
            "active_users_30d": 0,
            "total_news": 0,
            "news_7d": 0,
            "total_feedbacks": 0,
            "likes_count": 0,
            "dislikes_count": 0,
            "active_sources": 0
        }
        
        try:
            # 1. Usuarios Totales
            res_users = self.client.table("profiles").select("id", count="exact").execute()
            metrics["total_users"] = res_users.count if res_users.count else 0
            
            # 2. Usuarios Activos (Últimos 30 días)
            fecha_30d = (datetime.utcnow() - timedelta(days=30)).isoformat()
            res_active = self.client.table("profiles").select("id", count="exact").gt("updated_at", fecha_30d).execute()
            metrics["active_users_30d"] = res_active.count if res_active.count else 0
            
            # 3. Noticias Totales
            res_news = self.client.table("noticias").select("id", count="exact").execute()
            metrics["total_news"] = res_news.count if res_news.count else 0
            
            # 4. Noticias de los últimos 7 días
            fecha_7d = (datetime.utcnow() - timedelta(days=7)).isoformat()
            res_news_7d = self.client.table("noticias").select("id", count="exact").gt("scraped_at", fecha_7d).execute()
            metrics["news_7d"] = res_news_7d.count if res_news_7d.count else 0
            
            # 5. Feedbacks Agrupados
            res_fb = self.client.table("news_feedback").select("feedback").execute()
            if res_fb.data:
                likes = sum(1 for f in res_fb.data if f.get("feedback") == "like")
                dislikes = sum(1 for f in res_fb.data if f.get("feedback") == "dislike")
                metrics["total_feedbacks"] = len(res_fb.data)
                metrics["likes_count"] = likes
                metrics["dislikes_count"] = dislikes
                
            # 6. Fuentes RSS Activas
            res_config = self.client.table("app_config").select("rss_sources").eq("id", 1).single().execute()
            if res_config.data and "rss_sources" in res_config.data:
                metrics["active_sources"] = len(res_config.data["rss_sources"] or [])
                
            return metrics
            
        except Exception as e:
            logger.error(f"Error recopilando métricas de Admin: {e}")
            return metrics
            
    # ------------------------------------------------------------------ #
    #                NOTIFICACIONES: Noticias para Teams                  #
    # ------------------------------------------------------------------ #

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
            
    # ------------------------------------------------------------------ #
    #                CONFIGURACION: Parametros Globales SaaS              #
    # ------------------------------------------------------------------ #

    def get_app_config(self) -> dict:
        """Obtiene la configuración global de la aplicación desde la base de datos."""
        try:
            response = self.client.table("app_config").select("*").eq("id", 1).single().execute()
            return response.data if response.data else {}
        except Exception as e:
            logger.error(f"Error obteniendo app_config de DB: {e}")
            return {}

    def update_app_config(self, config_data: dict) -> dict:
        """Actualiza la configuración global de la aplicación en la base de datos."""
        try:
            # Aseguramos que siempre actualizamos la fila id=1
            config_data['updated_at'] = datetime.utcnow().isoformat()
            response = self.client.table("app_config").update(config_data).eq("id", 1).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error actualizando app_config de DB: {e}")
            raise e
            
# ------------------------------------------------------------------ #
#                SINGLETON: Punto de Acceso Global                    #
# ------------------------------------------------------------------ #

_supabase_service_instance = None

def get_supabase_service() -> SupabaseService:
    global _supabase_service_instance
    if _supabase_service_instance is None:
        _supabase_service_instance = SupabaseService()
    return _supabase_service_instance

def get_supabase_client():
    return get_supabase_service().client
