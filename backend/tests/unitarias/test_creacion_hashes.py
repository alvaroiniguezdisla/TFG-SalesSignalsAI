# ----------------------------------------------------------------------------------
# TEST DE HASHES (IDs DE LAS NOTICIAS)
# Qué hace esto: Comprueba que cuando llega una noticia, le generamos un ID unico (Hash)
# basado en su URL. Si la URL es la misma, el ID debe ser el mismo.
# Para qué sirve: Para no guardar la misma noticia dos veces si la descargamos de nuevo.
# ----------------------------------------------------------------------------------

import pytest 
from app.services.extraccion.scraper import hash_url

# Test basico para comprobar que el hash funciona bien
def test_hash_consistencia():
    url = "https://ejemplo.com/noticia-importante-2026"

    # Calculamos dos veces
    h1 = hash_url(url)
    h2 = hash_url(url)

    # Tienen que ser iguales
    assert h1 == h2

    # Y la longitud tiene que ser 32 chars (md5)
    assert len(h1) == 32

def test_hash_unicidad():
    # Dos urls distintas dan hashes distintos
    url1 = "https://ejemplo.com/una"
    url2 = "https://ejemplo.com/otra"
    
    h1 = hash_url(url1)
    h2 = hash_url(url2)

    assert h1 != h2


    

    
