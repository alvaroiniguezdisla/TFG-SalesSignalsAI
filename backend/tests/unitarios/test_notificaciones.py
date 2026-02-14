# ----------------------------------------------------------------------------------
# TEST DEL FILTRADO DE NOTIFICACIONES
#
# Objetivo: Verificar que el sistema de notificaciones filtra correctamente
# las noticias segun las preferencias del usuario (empresas y categorias).
#
# Que comprueba:
#   1. Que un usuario recibe noticias de sus empresas favoritas.
#   2. Que un usuario recibe noticias de sus categorias favoritas.
#   3. Que un usuario sin preferencias no recibe nada.
#   4. Que el filtro combinado (empresa + categoria) usa logica OR.
#   5. Que la comparacion es case-insensitive (mayusculas/minusculas).
# ----------------------------------------------------------------------------------

from app.services.notificaciones.notificador import filtrar_noticias_para_usuario


# Datos de prueba compartidos: 3 noticias con perfiles muy distintos
NOTICIAS_TEST = [
    {
        "titulo": "Santander abre nueva sede en Madrid",
        "empresas_clave_ia": ["Santander"],
        "categoria_ia": "Expansion / Crecimiento",
        "categoria_producto_ia": "Soluciones Empresariales",
        "relevancia_ia": 85
    },
    {
        "titulo": "Torneo de eSports en Barcelona",
        "empresas_clave_ia": ["ESL Gaming"],
        "categoria_ia": "Sin Interes Comercial",
        "categoria_producto_ia": "Gaming / OMEN",
        "relevancia_ia": 60
    },
    {
        "titulo": "Gobierno aprueba nueva ley de educacion",
        "empresas_clave_ia": [],
        "categoria_ia": "Sin Interes Comercial",
        "categoria_producto_ia": "Otros / No Aplica",
        "relevancia_ia": 10
    }
]


def test_filtrar_por_empresa():
    """
    Un usuario que sigue a 'Santander' solo recibe la noticia
    donde la IA detecto a Santander como empresa clave.
    Las otras 2 noticias (eSports y politica) se descartan.
    """
    perfil = {
        "favorite_companies": ["Santander"],
        "favorite_categories": []
    }

    resultado = filtrar_noticias_para_usuario(NOTICIAS_TEST, perfil)

    assert len(resultado) == 1
    assert "Santander" in resultado[0]["titulo"]


def test_filtrar_por_categoria():
    """
    Un usuario interesado en 'Gaming' recibe la noticia del torneo.
    Funciona porque 'Gaming' esta contenido en 'Gaming / OMEN'
    (la comparacion usa 'in', no igualdad exacta).
    """
    perfil = {
        "favorite_companies": [],
        "favorite_categories": ["Gaming"]
    }

    resultado = filtrar_noticias_para_usuario(NOTICIAS_TEST, perfil)

    assert len(resultado) == 1
    assert "eSports" in resultado[0]["titulo"]


def test_sin_preferencias_no_recibe_nada():
    """
    Si un usuario no ha configurado ni empresas ni categorias,
    no recibe ninguna notificacion. Esto evita enviar spam
    a usuarios que acaban de registrarse.
    """
    perfil = {
        "favorite_companies": [],
        "favorite_categories": []
    }

    resultado = filtrar_noticias_para_usuario(NOTICIAS_TEST, perfil)

    assert len(resultado) == 0


def test_filtrar_combinado_empresa_y_categoria():
    """
    Un usuario con empresa Y categoria favoritas recibe
    todas las que coincidan con ALGUNA de las dos (logica OR).
    Santander coincide por empresa, eSports por categoria.
    La de politica no coincide con ninguna.
    """
    perfil = {
        "favorite_companies": ["Santander"],
        "favorite_categories": ["Gaming"]
    }

    resultado = filtrar_noticias_para_usuario(NOTICIAS_TEST, perfil)

    assert len(resultado) == 2
    titulos = [n["titulo"] for n in resultado]
    assert any("Santander" in t for t in titulos)
    assert any("eSports" in t for t in titulos)


def test_filtrar_case_insensitive():
    """
    La comparacion debe ser case-insensitive: un usuario que escribe
    'santander' (minusculas) debe coincidir con 'Santander' (mayusculas)
    en empresas_clave_ia.
    """
    perfil = {
        "favorite_companies": ["santander"],
        "favorite_categories": []
    }

    resultado = filtrar_noticias_para_usuario(NOTICIAS_TEST, perfil)

    assert len(resultado) == 1
    assert "Santander" in resultado[0]["titulo"]
