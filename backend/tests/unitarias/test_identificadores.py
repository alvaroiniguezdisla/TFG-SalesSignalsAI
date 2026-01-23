import pytest 
from app.services.extraccion.scraper import hash_url

def test_hash_url_consistency():
    """
    OBJETIVO:Verificar que la misma URL siempre genera el mismo Hash (ID).
    Si esto falla, tendríamos noticias duplicadas en la base de datos.
    """
    url_prueba = "https://ejemplo.com/noticia-importante-2026"

    #Calculamos el mismo hash dos veces para la misma URL 

    hash1= hash_url(url_prueba)
    hash2= hash_url(url_prueba)

    #1. Verificamos que el hash sea consistente
    assert hash1 == hash2, "Error: El hash no es consistente, ha generado un hash diferente para la misma URL"

    print("Test de Consistencia de Hash: PASADO")

    #2. Verificamos longitud  MD5 (32 caracteres)
    assert len(hash1) == 32, f"Error: El hash no tiene la longitud correcta (MD5): {len(hash1)} caracteres"
    
    print("Test de Longitud de Hash: PASADO")

    #3. Verificamos que el hash sea único para dos URLs distintas
    url_distinta = "https://ejemplo.com/otra-noticia-2026"
    hash3 = hash_url(url_distinta)

    assert hash1 != hash3, "Error: El hash no es único, ha generado el mismo hash para dos URLs diferentes"

    print("Test de Unicidad de Hash: PASADO")

    

    
 