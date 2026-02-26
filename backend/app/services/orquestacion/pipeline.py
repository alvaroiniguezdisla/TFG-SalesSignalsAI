from app.services.extraccion.manager import get_extractor_manager
from bs4 import BeautifulSoup
from app.services.inteligencia import LlmService
from app.services.almacenamiento import SupabaseService
from pydantic import ValidationError
from app.schemas.noticia import Noticia
import logging

logger = logging.getLogger(__name__)

class NewsPipeline:
    def __init__(self):
        self.db = SupabaseService()
        self.llm= LlmService()

    def ejecutar(self):
        logger.info("[PIPELINE] ===============================================")
        logger.info("[PIPELINE] INICIANDO ORQUESTACION DE SEÑALES DE VENTA B2B ")
        logger.info("[PIPELINE] ===============================================")

        # 1. Hacemos ingesta de noticias 
        logger.info("[PIPELINE] Fase 1: Extraccion Multifuente (Scraper/RSS/Browser)")
        extractor = get_extractor_manager()
        noticias_crudas = extractor.obtener_noticias()

        # Si una fuente externa falla/bloquea, lo notificamos sin cortar la ejecución.
        fuentes_caidas = []
        get_fuentes_caidas = getattr(extractor, "get_ultimas_fuentes_caidas", None)
        if callable(get_fuentes_caidas):
            try:
                resultado = get_fuentes_caidas()
                if isinstance(resultado, list):
                    fuentes_caidas = resultado
            except Exception:
                fuentes_caidas = []

        if fuentes_caidas:
            nombres = ", ".join(item.get("fuente", "Desconocida") for item in fuentes_caidas)
            logger.warning(
                f"[EXTRACCION] {len(fuentes_caidas)} fuente(s) con incidencias: {nombres}"
            )
            for item in fuentes_caidas:
                detalle = "; ".join(item.get("errores", []))
                logger.warning(f"[EXTRACCION_FALLO] {item.get('fuente', 'Desconocida')}: {detalle}")

        if not noticias_crudas:
            logger.error("[PIPELINE] No se recolectaron noticias de ninguna fuente. Abortando.")
            return
        
        logger.info(f"[PIPELINE] Total de noticias capturadas (en crudo): {len(noticias_crudas)}")

        logger.info("[PIPELINE] Fase 2: Validacion de Datos (Pydantic)")
        noticias_validadas = []
        for noti_dict in noticias_crudas:
            try:
                # Pydantic lanza excepcion si faltan campos obligatorios
                noticia_obj = Noticia(**noti_dict)
                noticias_validadas.append(noticia_obj.model_dump())
            except ValidationError as e:
                # Recopilar solo los campos que han fallado para no saturar el log
                errores_campo = [err["loc"][0] for err in e.errors()]
                logger.error(f"[VALIDACION_ERROR] Noticia omitida. Campos corruptos: {errores_campo}")
                continue
                
        logger.info(f"[PIPELINE] {len(noticias_validadas)} noticias superaron los validadores de Schema.")

        noticias_enriquecidas= []

        # 2. Analizamos una a una 
        logger.info("[PIPELINE] Fase 3: Analisis de Inteligencia Artificial (LLM)")
        for idx, noticia in enumerate(noticias_validadas, 1):
            try:
                # Validacion de contenido: Intentar obtener texto para analizar
                raw_content = noticia.get('raw_content', '')
                
                if raw_content:
                    # --- LIMPIEZA DE TEXTO (si hay raw_content) ---
                    soup = BeautifulSoup(raw_content, 'html.parser')
                    texto_limpio = soup.get_text(separator=' ', strip=True)
                else:
                    # --- FALLBACK: usar título + resumen ---
                    titulo = noticia.get('titulo', '')
                    resumen = noticia.get('resumen', '')
                    texto_limpio = f"{titulo}. {resumen}".strip()
                    
                    if not texto_limpio or texto_limpio == ".":
                        logger.warning(f"[IA_SKIP] - [{idx}/{len(noticias_validadas)}] Sin contenido extraible.")
                        continue
                    
                    logger.debug("[IA_FALLBACK] - Extraccion alternativa empleada.")

                logger.info(f"[IA_ANALISIS] Procesando [{idx}/{len(noticias_validadas)}]: {noticia['titulo'][:60]}...") 
                
                # Llamada protegida a la IA
                analisis = self.llm.analizar_oportunidad(noticia['titulo'], texto_limpio)

                if analisis:
                    noticia['categoria_ia'] = analisis.get('categoria', 'Sin clasificar')
                    noticia['categoria_producto_ia'] = analisis.get('categoria_producto', 'Otros / No Aplica')
                    noticia['relevancia_ia'] = analisis.get('relevancia', 0)
                    noticia['resumen_comercial_ia'] = analisis.get('resumen_comercial', '')
                    noticia['talk_track_ia'] = analisis.get('talk_track', '')
                    noticia['email_draft_ia'] = analisis.get('email_draft', '')

                    # Empresas
                    empresas_raw = analisis.get('empresas', [])
                    noticia['empresas_clave_ia'] = [
                        e.get('nombre', e) if isinstance(e, dict) else e
                        for e in empresas_raw
                    ]
                    noticia['empresas_detalle_ia'] = empresas_raw
                    
                    logger.info(f"[IA_RESULTADO] Score: {noticia['relevancia_ia']}/100 | Categoria: {noticia['categoria_ia']}")
                else:
                    logger.error(f"[IA_FALLO] El modelo no devolvio un JSON valido para: {noticia['titulo'][:40]}...")
                    noticia['categoria_ia'] = "Error IA"
                    noticia['categoria_producto_ia'] = "Error IA"
                    noticia['relevancia_ia'] = 0
                    noticia['resumen_comercial_ia'] = "No se pudo analizar"
                    noticia['empresas_clave_ia'] = []
                    noticia['empresas_detalle_ia'] = []
                    noticia['talk_track_ia'] = ''
                    noticia['email_draft_ia'] = ''

                noticias_enriquecidas.append(noticia)
            
            except Exception as e:
                logger.error(f"[IA_ERROR_FATAL] Error con noticia '{noticia.get('titulo', 'Unknown')[:30]}': {e}")
                continue

        # 4. Guardamos en la base de datos
        logger.info("[PIPELINE] Fase 4: Deduplicacion y Almacenamiento BD")
        
        self.db.insert_news_deduplicacion(noticias_enriquecidas)

        logger.info("[PIPELINE] ===============================================")
        logger.info(f"[PIPELINE] FINALIZADO EXITO: {len(noticias_enriquecidas)} procesadas.")
        logger.info("[PIPELINE] ===============================================")


if __name__ == "__main__":
    pipeline = NewsPipeline()
    pipeline.ejecutar()
