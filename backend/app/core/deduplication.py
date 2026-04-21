import difflib
import logging
import json

logger = logging.getLogger(__name__)

def es_titulo_similar(titulo1: str, titulo2: str, umbral: float = 0.85) -> bool:
    """Devuelve True si los títulos son 'iguales' (>Umbral Configurado similitud)."""
    if not titulo1 or not titulo2:
        return False
        
    ratio = difflib.SequenceMatcher(None, titulo1, titulo2).ratio()
    
    return ratio > umbral

def fusionar_datos_noticia(existente: dict, nueva: dict) -> bool:
    cambios = False
    
    # 1. Conservar Fuente Original
    # En el modelo estructurado, la fuente principal se mantiene intacta y no se concatena.
    fuente_nueva = nueva.get('fuente', '')
    
    # 2. Fusionar URLs (Añadiendo Fuentes Secundarias)
    # Si viene vacía o nula, inicializamos como lista vacía
    if not isinstance(existente.get('urls_extra'), list):
        # Manejo de retrocompatibilidad para registros anteriores en formato string
        try:
            val = existente.get('urls_extra')
            existente['urls_extra'] = json.loads(val) if isinstance(val, str) else []
        except Exception:
            existente['urls_extra'] = []
    
    url_nueva = nueva.get('url')
    
    if url_nueva and fuente_nueva:
        # Buscar si la URL ya existe dentro del array de objetos JSON
        url_existe = any(
            isinstance(obj, dict) and obj.get("url") == url_nueva 
            for obj in existente['urls_extra']
        )
        
        # O si la URL nueva es exactamente la de la noticia principal
        url_es_principal = (existente.get('url') == url_nueva)
        
        if not url_existe and not url_es_principal:
            existente['urls_extra'].append({
                "fuente": fuente_nueva,
                "url": url_nueva
            })
            cambios = True
            
    return cambios