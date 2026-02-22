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
        logger.info("[PIPELINE] Iniciando proceso de ingesta y categorización de noticias...")

        #1. Hacemos ingesta de noticias 
        noticias_crudas = get_extractor_manager().obtener_noticias()

        if not noticias_crudas:
            logger.warning("[PIPELINE] No se han podido obtener noticias")
            return
        
        logger.info(f"[PIPELINE] Se han obtenido {len(noticias_crudas)} noticias")

        noticias_validadas = []
        for noti_dict in noticias_crudas:
            try:
                # Pydantic lanza excepcion si faltan campos obligatorios
                noticia_obj = Noticia(**noti_dict)
                noticias_validadas.append(noticia_obj.model_dump())
            except ValidationError as e:
                # Recopilar solo los campos que han fallado para no saturar el log
                errores_campo = [err["loc"][0] for err in e.errors()]
                logger.error(f"[PIPELINE] Noticia omitida por estructura inválida. Campos corruptos: {errores_campo}")
                continue
                
        logger.info(f"[PIPELINE] {len(noticias_validadas)} noticias han pasado el filtro estricto de Pydantic")

        noticias_enriquecidas= []

        # 2. Analizamos una a una 
        for noticia in noticias_validadas:
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
                        logger.warning("Saltando noticia: sin contenido, título ni resumen disponible")
                        continue
                    
                    logger.info(f"Usando fallback (título+resumen) para: {titulo[:40]}...")

                logger.info(f"Analizando con IA: {noticia['titulo'][:50]}...") 
                
                # Llamada protegida a la IA
                analisis = self.llm.analizar_oportunidad(noticia['titulo'], texto_limpio)

                if analisis:
                    noticia['categoria_ia'] = analisis.get('categoria', 'Sin clasificar')
                    noticia['categoria_producto_ia'] = analisis.get('categoria_producto', 'Otros / No Aplica')
                    noticia['relevancia_ia'] = analisis.get('relevancia', 0)
                    noticia['resumen_comercial_ia'] = analisis.get('resumen_comercial', '')
                    noticia['talk_track_ia'] = analisis.get('talk_track', '')
                    noticia['email_draft_ia'] = analisis.get('email_draft', '')

                    # Empresas: ahora la IA devuelve list[dict] con {nombre, tamano}
                    empresas_raw = analisis.get('empresas', [])
                    noticia['empresas_clave_ia'] = [
                        e.get('nombre', e) if isinstance(e, dict) else e
                        for e in empresas_raw
                    ]
                    noticia['empresas_detalle_ia'] = empresas_raw
                else:
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
                logger.error(f"Error procesando noticia '{noticia.get('titulo', 'Unknown')[:30]}': {e}")
                continue

        #4. Guardamos en la base de datos
        logger.info("Guardando noticias en la base de datos...")
        
        self.db.insert_news_deduplicacion(noticias_enriquecidas)

        logger.info(f"Se han guardado {len(noticias_enriquecidas)} noticias")


if __name__ == "__main__":
    pipeline = NewsPipeline()
    pipeline.ejecutar()