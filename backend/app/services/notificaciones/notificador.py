"""
Servicio de notificaciones.
Filtra noticias por preferencias de usuario y envía emails personalizados.
"""
import time
import logging
from datetime import datetime, timedelta
from app.services.almacenamiento.database import supabase
from app.services.notificaciones.email_service import email_service

logger = logging.getLogger(__name__)

# Configuración para evitar bloqueos de Gmail
MAX_EMAILS_POR_EJECUCION = 50
DELAY_ENTRE_EMAILS = 1  # segundos


def obtener_usuarios_con_preferencias():
    """Obtiene todos los usuarios con sus preferencias desde Supabase."""
    try:
        response = supabase.table("profiles").select("*").execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        return []


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
        # 1. Obtener noticias de las últimas 6 horas con relevancia >= 40
        hace_6h = (datetime.utcnow() - timedelta(hours=6)).isoformat()
        response = supabase.table("noticias")\
            .select("*")\
            .gt("scraped_at", hace_6h)\
            .gte("relevancia_ia", 40)\
            .order("relevancia_ia", desc=True)\
            .execute()
        
        noticias_recientes = response.data or []
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
            if enviados >= MAX_EMAILS_POR_EJECUCION:
                logger.warning(f"Limite de {MAX_EMAILS_POR_EJECUCION} emails alcanzado")
                break
                
            email = usuario.get("email")
            nombre = usuario.get("first_name") or "Usuario"
            
            if not email:
                continue

            # Filtrar noticias para este usuario
            noticias_usuario = filtrar_noticias_para_usuario(noticias_recientes, usuario)
            
            if noticias_usuario:
                logger.info(f"Enviando {len(noticias_usuario)} noticias a {email}")
                if email_service.enviar_resumen(email, nombre, noticias_usuario):
                    enviados += 1
                    # Delay para evitar bloqueos de Gmail
                    if enviados < len(usuarios):
                        time.sleep(DELAY_ENTRE_EMAILS)

        logger.info(f"Notificaciones enviadas: {enviados}")
        return enviados

    except Exception as e:
        logger.error(f"Error en envío de notificaciones: {e}")
        return 0
