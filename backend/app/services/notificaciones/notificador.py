"""
Servicio de notificaciones.
Filtra noticias por preferencias de usuario y envía emails personalizados.
"""
import time
import logging
from app.services.almacenamiento.database import get_supabase_service
from app.services.notificaciones.email_service import get_email_service

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
    logger.info("Iniciando envío de notificaciones por email...")

    try:
        db = get_supabase_service()
        app_config = db.get_app_config()
        max_emails = app_config.get("max_emails_ejecucion", 50)
        delay_emails = app_config.get("delay_entre_emails", 1)

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
            # Limite de emails por ejecucion
            if enviados >= max_emails:
                logger.warning(f"Limite de {max_emails} emails alcanzado")
                break
                
            email = usuario.get("email")
            nombre = usuario.get("first_name") or "Usuario"
            
            if not email:
                continue

            # Filtrar noticias para este usuario
            noticias_usuario = filtrar_noticias_para_usuario(noticias_recientes, usuario)
            
            if noticias_usuario:
                logger.info(f"Enviando {len(noticias_usuario)} noticias a {email}")
                if get_email_service().enviar_resumen(email, nombre, noticias_usuario):
                    enviados += 1
                    # Delay para evitar bloqueos de Gmail
                    if enviados < len(usuarios):
                        time.sleep(delay_emails)

        logger.info(f"Notificaciones enviadas: {enviados}")
        return enviados

    except Exception as e:
        logger.error(f"Error en envío de notificaciones: {e}")
        return 0

