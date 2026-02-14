# ----------------------------------------------------------------------------------
# TEST DE INTEGRACION: DEDUPLICACION REAL EN SUPABASE (CASO APPLE)
#
# Objetivo: Verificar que el sistema de deduplicacion funciona contra la base
# de datos real. Inserta una noticia y luego intenta meter otra casi identica
# (de otra fuente). El sistema debe fusionarlas, no duplicarlas.
#
# IMPORTANTE: Este test requiere conexion a Supabase real.
# Se ejecuta por separado de los tests unitarios:
#   python -m pytest tests/integracion/ -v
#
# Que comprueba:
#   1. Que dos titulos casi identicos se detectan como similares.
#   2. Que insert_news_deduplicacion fusiona la segunda noticia con la primera.
#   3. Que la noticia fusionada tiene las fuentes combinadas.
#   4. Que NO se crea una fila duplicada en la base de datos.
# ----------------------------------------------------------------------------------

import pytest
import time
from datetime import datetime

from app.services.almacenamiento.database import SupabaseService
from app.core.deduplication import es_titulo_similar


# --- Datos de prueba ---

NOTICIA_ORIGINAL = {
    "titulo": "Apple prepara una renovacion de su apuesta por la IA para recuperar la confianza inversora",
    "url": "https://cincodias.elpais.com/companias/2026-01-23/apple-prepara-renovacion.html",
    "fuente": "Cinco Dias",
    "scraped_at": datetime.now().isoformat(),
    "published_at": datetime.now().isoformat(),
    "categoria_ia": "Transformacion Digital",
    "relevancia_ia": 90,
    "resumen": "Apple busca recuperar la confianza de los inversores con una apuesta por la IA...",
    "resumen_comercial_ia": "Oportunidad para venta de servidores y hardware IA.",
    "empresas_clave_ia": ["Apple", "OpenAI"],
    "url_hash": "test_integracion_hash_apple_1"
}

NOTICIA_DUPLICADA = {
    "titulo": "Apple prepara una renovacion de su apuesta por la IA para recuperar la confianza",
    "url": "https://www.eleconomista.es/tecnologia/apple-renueva-apuesta-ia.html",
    "fuente": "El Economista",
    "scraped_at": datetime.now().isoformat(),
    "published_at": datetime.now().isoformat(),
    "categoria_ia": "Transformacion Digital",
    "relevancia_ia": 85,
    "resumen": "La compania de la manzana mordida invertira millones en IA generativa...",
    "resumen_comercial_ia": "Oportunidad para venta de consultoria estrategica.",
    "empresas_clave_ia": ["Apple"],
    "url_hash": "test_integracion_hash_apple_2"
}


@pytest.fixture
def db():
    """
    Fixture que proporciona una instancia de SupabaseService
    y limpia los datos de prueba al terminar (aunque el test falle).
    """
    servicio = SupabaseService()

    # Limpieza previa (por si quedo basura de una ejecucion anterior)
    _limpiar_datos_test(servicio)

    yield servicio

    # Limpieza posterior (garantizada aunque el test falle)
    _limpiar_datos_test(servicio)


def _limpiar_datos_test(db):
    """Elimina los datos de prueba de la base de datos."""
    try:
        db.client.table("noticias").delete().eq("url_hash", NOTICIA_ORIGINAL["url_hash"]).execute()
        db.client.table("noticias").delete().eq("url_hash", NOTICIA_DUPLICADA["url_hash"]).execute()
    except Exception:
        pass


def test_titulos_apple_son_similares():
    """
    Verifica que los dos titulos de Apple se detectan como similares
    ANTES de probar contra la base de datos.
    """
    assert es_titulo_similar(NOTICIA_ORIGINAL["titulo"], NOTICIA_DUPLICADA["titulo"])


def test_deduplicacion_real_en_supabase(db):
    """
    La prueba de fuego: inserta una noticia en Supabase, luego intenta
    meter otra casi identica. El sistema debe fusionarlas.
    """
    # 1. Insertar la noticia original directamente en la BD
    db.client.table("noticias").insert([NOTICIA_ORIGINAL]).execute()
    time.sleep(1)

    # 2. Intentar insertar la duplicada usando la funcion inteligente
    db.insert_news_deduplicacion([NOTICIA_DUPLICADA])
    time.sleep(1)

    # 3. La noticia duplicada NO deberia existir como fila independiente
    busqueda = db.client.table("noticias").select("*").eq(
        "url_hash", NOTICIA_DUPLICADA["url_hash"]
    ).execute()
    assert len(busqueda.data) == 0, "La noticia duplicada NO deberia tener su propia fila"

    # 4. La noticia original debe tener ahora las dos fuentes fusionadas
    original = db.client.table("noticias").select("*").eq(
        "url_hash", NOTICIA_ORIGINAL["url_hash"]
    ).execute()
    assert len(original.data) == 1, "La noticia original debe seguir existiendo"

    item = original.data[0]
    assert "El Economista" in item["fuente"], (
        f"La fuente fusionada deberia incluir 'El Economista', pero es: {item['fuente']}"
    )
