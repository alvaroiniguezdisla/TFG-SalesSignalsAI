import difflib
import logging
logger = logging.getLogger(__name__)

SIMILITUD_UMBRAL = 0.85

def es_titulo_similar(titulo1: str, titulo2: str) -> bool:
    """Devuelve True si los títulos son 'iguales' (>85% similitud)."""
    if not titulo1 or not titulo2:
        return False
    
    ratio = difflib.SequenceMatcher(None, titulo1, titulo2).ratio()
    
    return ratio > SIMILITUD_UMBRAL

def fusionar_datos_noticia(existente: dict, nueva: dict) -> bool:
    """
    Mezcla los datos de 'nueva' dentro de 'existente'.
    Devuelve True si hubo cambios.
    """
    cambios = False
    
    # 1. Fusionar Fuente 
    fuente_actual = existente.get('fuente', '')
    fuente_nueva = nueva.get('fuente', '')
    
    if fuente_nueva and fuente_nueva not in fuente_actual:
        existente['fuente'] = f"{fuente_actual} + {fuente_nueva}"
        cambios = True
    
    # 2. Fusionar URLs
    if 'urls_extra' not in existente or existente['urls_extra'] is None:
        existente['urls_extra'] = []
    
    url_nueva = nueva.get('url')
    if url_nueva and url_nueva not in existente['urls_extra']:
        existente['urls_extra'].append(url_nueva)
        cambios = True
        
    return cambios