# ----------------------------------------------------------------------------------
# TEST DE GENERACION DE IDENTIFICADORES (HASHES)
#
# Objetivo: Verificar que la funcion hash_url genera identificadores unicos y
# consistentes para cada noticia, basados en su URL.
#
# Que comprueba:
#   1. Que la misma URL siempre produce el mismo hash (consistencia).
#   2. Que el hash tiene la longitud correcta de MD5 (32 caracteres hex).
#   3. Que dos URLs distintas producen hashes distintos (unicidad).
#   4. Que URLs con caracteres especiales (acentos, ñ) se hashean sin error.
#   5. Que el hash solo contiene caracteres hexadecimales validos.
#
# Por que es importante: Si los hashes no son consistentes, el sistema guardaria
# la misma noticia varias veces en la base de datos.
# ----------------------------------------------------------------------------------

from app.core.utils import hash_url


def test_hash_consistencia():
    """
    La misma URL siempre genera el mismo hash.
    Si esto fallara, cada vez que el scraper descargara la misma noticia,
    la trataria como nueva y la duplicaria en la base de datos.
    """
    url = "https://ejemplo.com/noticia-importante-2026"

    hash_1 = hash_url(url)
    hash_2 = hash_url(url)

    assert hash_1 == hash_2


def test_hash_longitud_md5():
    """
    El hash tiene exactamente 32 caracteres, que es el formato
    estandar de MD5 (128 bits representados en hexadecimal).
    """
    url = "https://ejemplo.com/noticia-importante-2026"

    resultado = hash_url(url)

    assert len(resultado) == 32


def test_hash_unicidad():
    """
    Dos URLs distintas generan hashes distintos.
    Si esto fallara, dos noticias diferentes se confundirian
    como si fueran la misma.
    """
    url_1 = "https://ejemplo.com/noticia-una"
    url_2 = "https://ejemplo.com/noticia-otra"

    hash_1 = hash_url(url_1)
    hash_2 = hash_url(url_2)

    assert hash_1 != hash_2


def test_hash_caracteres_hexadecimales():
    """
    El hash solo contiene caracteres hexadecimales (0-9, a-f).
    Si contuviera caracteres raros, podria causar problemas al usarlo
    como clave en Supabase o como parte de una URL en la API.
    """
    url = "https://ejemplo.com/noticia"

    resultado = hash_url(url)

    assert all(c in "0123456789abcdef" for c in resultado)


def test_hash_url_con_caracteres_especiales():
    """
    URLs con caracteres españoles (acentos, ñ, etc.) se hashean
    sin errores. Esto es importante porque nuestras fuentes son
    periodicos españoles que pueden tener URLs con estos caracteres.
    """
    url_acento = "https://elpais.com/economía/expansión-empresarial"
    url_enie = "https://eleconomista.es/españa/año-2026"

    hash_acento = hash_url(url_acento)
    hash_enie = hash_url(url_enie)

    assert len(hash_acento) == 32
    assert len(hash_enie) == 32
    assert hash_acento != hash_enie
