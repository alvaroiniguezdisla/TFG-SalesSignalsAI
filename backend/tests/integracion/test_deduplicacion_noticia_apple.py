# ----------------------------------------------------------------------------------
# TEST DE INTEGRACION REAL: CASO APPLE (LA PRUEBA DE FUEGO)
# Qué hace esto: Simula todo el proceso con una noticia real (Apple) y comprueba
# que si metemos una noticia casi igual (pero de otra fuente), el sistema NO la duplica.
# Para qué sirve: Es la prueba definitiva de que la deduplicación funciona en la base de datos.
# ----------------------------------------------------------------------------------

import pytest
import sys
import os
import asyncio
from datetime import datetime

# Añadir root al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.almacenamiento.database import SupabaseService
from app.core.deduplication import es_titulo_similar

# Datos de prueba para el caso Apple
# Noticia 1: La que ya tendriamos guardada
NOTICIA_ORIGINAL = {
    "titulo": "Apple prepara una renovación de su apuesta por la IA para recuperar la confianza inversora",
    "url": "https://cincodias.elpais.com/companias/2026-01-23/apple-prepara-renovacion.html", 
    "fuente": "Cinco Días (Compañías)",
    "scraped_at": datetime.now().isoformat(),
    "published_at": datetime.now().isoformat(),
    "categoria_ia": "Transformación Digital",
    "relevancia_ia": 90,
    "resumen": "Apple busca recuperar la confianza de los inversores con una fuerte apuesta por la IA...",
    "resumen_comercial_ia": "Venderemos servidores, hardware y software para implementar Siri...",
    "empresas_clave_ia": ["Apple", "OpenAI"],
    "url_hash": "hash_apple_1"
}

# Noticia 2: Una nueva que es casi igual pero de otra fuente
NOTICIA_NUEVA = {
    "titulo": "Apple prepara una renovación de su apuesta por la IA para recuperar la confianza", 
    "url": "https://www.eleconomista.es/tecnologia/apple-renueva-apuesta-ia.html", 
    "fuente": "El Economista", 
    "scraped_at": datetime.now().isoformat(),
    "published_at": datetime.now().isoformat(),
    "resumen": "La compañía de la manzana mordida invertirá millones en IA generativa...",
    "resumen_comercial_ia": "Oportunidad para venta de consultoría estratégica...",
    "empresas_clave_ia": ["Apple"],
    "categoria_ia": "Transformación Digital",
    "relevancia_ia": 85,
    "url_hash": "hash_apple_2"
}

@pytest.mark.asyncio
async def test_deduplicacion_apple():
    
    db = SupabaseService()
    
    # 1. Limpiamos por si acaso (Borramos por titulo para asegurar que no quedan restos viejos)
    try:
        db.client.table("noticias").delete().eq("titulo", NOTICIA_ORIGINAL["titulo"]).execute()
        db.client.table("noticias").delete().eq("url_hash", NOTICIA_ORIGINAL["url_hash"]).execute()
        db.client.table("noticias").delete().eq("url_hash", NOTICIA_NUEVA["url_hash"]).execute()
    except:
        pass

    # 2. Insertamos la primera a mano "a la fuerza" para asegurar que existe
    db.client.table("noticias").insert([NOTICIA_ORIGINAL]).execute()
    
    await asyncio.sleep(2) # Damos tiempo

    # 3. Comprobamos que el sistema detecta que son parecidas
    es_similar = es_titulo_similar(NOTICIA_ORIGINAL["titulo"], NOTICIA_NUEVA["titulo"])
    assert es_similar == True

    # 4. Intentamos meter la segunda usando la funcion inteligente
    # Deberia detectar que es duplicada y NO crear una fila nueva, sino actualizar la vieja
    db.insert_news_deduplicacion([NOTICIA_NUEVA])
    
    await asyncio.sleep(2) 

    # 5. Comprobamos resultado
    # Buscamos por el hash de la segunda. No deberia estar (porque se fusiono con la primera)
    busqueda = db.client.table("noticias").select("*").eq("url_hash", NOTICIA_NUEVA["url_hash"]).execute()
    assert len(busqueda.data) == 0
    
    # Buscamos la original. Deberia tener ahora las dos fuentes
    final = db.client.table("noticias").select("*").eq("url_hash", NOTICIA_ORIGINAL["url_hash"]).execute()
    item = final.data[0]
    
    # Tiene que salir El Economista en la fuente
    assert "El Economista" in item["fuente"]

