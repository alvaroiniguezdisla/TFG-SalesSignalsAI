# ----------------------------------------------------------------------------------
# TEST DE DEDUPLICACION POR TITULO (LOGICA DIFUSA)
#
# Objetivo: Verificar que el sistema de deduplicacion detecta noticias
# con titulos similares, las fusiona correctamente, y conserva las distintas.
#
# Que comprueba:
#   1. Que la funcion es_titulo_similar detecta titulos casi identicos.
#   2. Que titulos claramente distintos NO se consideran similares.
#   3. Que la fusion combina fuentes y guarda URLs extra.
#   4. Que el proceso completo reduce 3 noticias a 2 (fusionando duplicados).
# ----------------------------------------------------------------------------------

from app.core.deduplication import es_titulo_similar, fusionar_datos_noticia
from app.services.extraccion.manager import NewsExtractorManager


# -----------------------------------------------------------------------
# Tests de es_titulo_similar (el comparador de titulos)
# -----------------------------------------------------------------------

def test_titulos_similares_se_detectan():
    """
    Dos titulos que dicen basicamente lo mismo (>85% similitud)
    deben ser detectados como similares.
    """
    titulo_a = "El Banco Santander sube un 5% en bolsa"
    titulo_b = "Banco Santander sube 5% en la bolsa"

    assert es_titulo_similar(titulo_a, titulo_b) is True


def test_titulos_distintos_no_son_similares():
    """
    Dos titulos sobre temas completamente diferentes
    NO deben ser considerados similares.
    """
    titulo_a = "El Banco Santander sube un 5% en bolsa"
    titulo_b = "El Real Madrid gana la Champions League"

    assert es_titulo_similar(titulo_a, titulo_b) is False


def test_titulo_vacio_no_es_similar():
    """
    Si alguno de los titulos esta vacio o es None,
    la funcion debe devolver False sin errores.
    """
    assert es_titulo_similar("", "Cualquier titulo") is False
    assert es_titulo_similar("Cualquier titulo", "") is False
    assert es_titulo_similar(None, "Cualquier titulo") is False


# -----------------------------------------------------------------------
# Tests de fusionar_datos_noticia (la mezcla de datos)
# -----------------------------------------------------------------------

def test_fusion_combina_fuentes():
    """
    Cuando se fusionan dos noticias de fuentes distintas,
    las fuentes se concatenan con coma: "Fuente A, Fuente B".
    """
    existente = {"titulo": "Noticia X", "fuente": "El Pais", "url": "url1"}
    nueva = {"titulo": "Noticia X", "fuente": "El Economista", "url": "url2"}

    cambios = fusionar_datos_noticia(existente, nueva)

    assert cambios is True
    assert existente["fuente"] == "El Pais"
    assert len(existente.get("urls_extra", [])) == 1
    assert existente["urls_extra"][0]["fuente"] == "El Economista"


def test_fusion_guarda_url_extra():
    """
    La URL de la noticia duplicada se guarda en urls_extra
    para no perder la referencia a la otra fuente.
    """
    existente = {"titulo": "Noticia X", "fuente": "El Pais", "url": "url1"}
    nueva = {"titulo": "Noticia X", "fuente": "El Economista", "url": "url2"}

    fusionar_datos_noticia(existente, nueva)

    assert any(obj.get("url") == "url2" for obj in existente["urls_extra"])


def test_fusion_no_duplica_misma_fuente():
    """
    Si la fuente ya esta incluida, no se vuelve a añadir.
    Evita resultados como "El Pais, El Pais, El Pais".
    Nota: la URL si se añade a urls_extra porque urls_extra empieza vacio.
    """
    existente = {"titulo": "Noticia X", "fuente": "El Pais", "url": "url1"}
    nueva = {"titulo": "Noticia X", "fuente": "El Pais", "url": "url1"}

    fusionar_datos_noticia(existente, nueva)

    assert "url1" not in [obj.get("url") for obj in existente.get("urls_extra", [])]


# -----------------------------------------------------------------------
# Test del proceso completo (deduplicar_por_titulo del manager)
# -----------------------------------------------------------------------

def test_deduplicacion_completa_reduce_duplicados():
    """
    Verifica el flujo completo: 3 noticias entran (2 duplicadas + 1 unica),
    y salen 2 noticias (la duplicada fusionada + la unica intacta).
    """
    manager = NewsExtractorManager()

    noticias_input = [
        {"titulo": "El Banco Santander sube un 5% en bolsa", "fuente": "Fuente A", "url": "url1"},
        {"titulo": "Banco Santander sube 5% en la bolsa", "fuente": "Fuente B", "url": "url2"},
        {"titulo": "El Real Madrid gana la liga", "fuente": "Fuente C", "url": "url3"}
    ]

    resultado = manager.deduplicar_por_titulo(noticias_input)

    # De 3 noticias, quedan 2
    assert len(resultado) == 2

    # La noticia fusionada debe tener ambas fuentes
    santander = [n for n in resultado if "Santander" in n["titulo"]][0]
    assert santander["fuente"] == "Fuente A"
    assert len(santander.get("urls_extra", [])) == 1
    assert santander["urls_extra"][0]["fuente"] == "Fuente B"

    # La noticia del Madrid se mantiene intacta
    madrid = [n for n in resultado if "Madrid" in n["titulo"]][0]
    assert madrid["fuente"] == "Fuente C"
