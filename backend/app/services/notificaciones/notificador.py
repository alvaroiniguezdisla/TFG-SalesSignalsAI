"""
Servicio de notificaciones.
Filtra noticias por preferencias de usuario y envía mensajes a Teams.
"""
import time
import logging
from app.services.almacenamiento.database import get_supabase_service
from app.services.notificaciones.teams_graph_service import get_teams_graph_service
from app.core.config import settings

logger = logging.getLogger(__name__)


def obtener_usuarios_con_preferencias():
    """Obtiene todos los usuarios con sus preferencias desde Supabase."""
    return get_supabase_service().obtener_usuarios_preferencias()


def filtrar_noticias_para_usuario(noticias: list, perfil: dict) -> list:
    """
    Filtra noticias según las preferencias del usuario.
    
    Args:
        noticias: Lista de todas las noticias recientes
        perfil: Perfil del usuario con sus preferencias
    
    Returns:
        Lista de noticias que coinciden con las preferencias
    """
    empresas = perfil.get("favorite_companies") or []
    categorias = perfil.get("favorite_categories") or []
    
    # Si no tiene preferencias, no le mandamos nada
    if not empresas and not categorias:
        return []

    resultado = []
    for n in noticias:
        # Coincidencia por empresa
        empresas_noticia = n.get("empresas_clave_ia") or []
        match_empresa = any(
            empresa.lower() in emp.lower()
            for empresa in empresas
            for emp in empresas_noticia
        )

        # Coincidencia por categoría (señal de negocio o producto)
        cat_noticia = (n.get("categoria_ia") or "").lower()
        prod_noticia = (n.get("categoria_producto_ia") or "").lower()
        match_categoria = any(
            cat.lower() in cat_noticia or cat.lower() in prod_noticia
            for cat in categorias
        )

        if match_empresa or match_categoria:
            resultado.append(n)

    return resultado


def enviar_notificaciones_a_todos():
    """
    Proceso principal: envía notificaciones a todos los usuarios.
    Se ejecuta después de cada ingesta del pipeline.
    """
    logger.info("Iniciando envío de notificaciones por Teams...")

    try:
        db = get_supabase_service()
        app_config = db.get_app_config()
        max_notifs = app_config.get("max_notificaciones_ejecucion", 50)
        delay_notifs = app_config.get("delay_entre_notificaciones", 1)
        target_email = (settings.TEAMS_TARGET_USER_EMAIL or "").strip().lower()

        if not target_email:
            logger.warning(
                "TEAMS_TARGET_USER_EMAIL no está configurado. "
                "No se enviarán notificaciones de Teams en esta ejecución."
            )
            return 0

        # 1. Obtener noticias de las últimas 6 horas con relevancia >= 40
        noticias_recientes = db.obtener_noticias_relevantes_recientes()
        
        logger.info(f"Noticias recientes (ultimas 6h, relevancia >= 40): {len(noticias_recientes)}")

        if not noticias_recientes:
            logger.info("No hay noticias nuevas para notificar.")
            return 0

        # 2. Obtener usuarios
        usuarios = obtener_usuarios_con_preferencias()
        logger.info(f"Usuarios registrados: {len(usuarios)}")

        if not usuarios:
            logger.info("No hay usuarios registrados.")
            return 0

        # 3. Enviar a cada usuario (con límite y delay)
        enviados = 0
        for usuario in usuarios:
            # Limite de notificaciones por ejecucion
            if enviados >= max_notifs:
                logger.warning(f"Limite de {max_notifs} notificaciones alcanzado")
                break
                
            email = usuario.get("email")
            nombre = usuario.get("first_name") or "Usuario"
            
            if not email:
                continue

            # Filtrar noticias para este usuario
            noticias_usuario = filtrar_noticias_para_usuario(noticias_recientes, usuario)
            
            if noticias_usuario:
                
                if email.lower() == target_email:
                    logger.info(f"Enviando {len(noticias_usuario)} noticias vía Teams a {email}")
                    if get_teams_graph_service().enviar_notificacion(email, nombre, noticias_usuario):
                        enviados += 1
                        # Delay para evitar rate limits
                        if enviados < len(usuarios):
                            time.sleep(delay_notifs)
                else:
                    logger.info(f"Omitiendo notificación a {email} (solo se alerta al usuario configurado ).")

        logger.info(f"Notificaciones enviadas: {enviados}")
        return enviados

    except Exception as e:
        logger.error(f"Error en envío de notificaciones: {e}")
        return 0

if __name__ == "__main__":
    # Forzamos que se vea el output por consola en la ejecución manual
    print("==================================================")
    print("   INICIANDO ENVÍO MANUAL DE NOTIFICACIONES...    ")
    print("==================================================")
    
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    enviados = enviar_notificaciones_a_todos()
    
    print("==================================================")
    print(f"    PROCESO TERMINADO. Bucle completado.       ")
    print("==================================================")
