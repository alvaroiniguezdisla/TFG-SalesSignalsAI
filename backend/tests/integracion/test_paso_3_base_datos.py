import sys
import os
import time
import hashlib
from datetime import datetime

# Fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.almacenamiento.database import supabase_service

def ejecutar_prueba_base_datos():
    print("\n")
    print(" INICIO DE PRUEBA: BASE DE DATOS Y DEDUPLICACION")
    print("\n")
    
    # 1. Creamos una noticia falsa
    timestamp = int(time.time())
    url_fake = f"http://test.com/noticia-{timestamp}"
    # Generamos hash MD5 (Simulando lo que hace el scraper)
    url_hash_fake = hashlib.md5(url_fake.encode('utf-8')).hexdigest()

    noticia_fake = {
        "titulo": f"Noticia de Prueba {timestamp}",
        "url": url_fake,
        "url_hash": url_hash_fake, # CAMPO OBLIGATORIO
        "fuente": "TestSource A",
        "scraped_at": datetime.now().isoformat(),
        
        # Campos de IA vacíos o dummy para que no falle el insert
        "categoria_ia": "Test",
        "relevancia_ia": 50,
        "raw_content": "Contenido dummy para test",
        "resumen": "Resumen dummy",
        "empresas_clave_ia": [],
        "resumen_comercial_ia": "Resumen comercial dummy"
    }
    
    print(f"1. Insertando noticia original: '{noticia_fake['titulo']}'...")
    response_1 = supabase_service.insert_news_deduplicacion([noticia_fake])
    
    if response_1:
         print("   -> Insercion correcta.")
    
    print("   Esperando 2 segundos para simular el paso del tiempo...")
    time.sleep(2)
    
    # 2. Insertamos la MISMA noticia pero con otra fuente (Gemela)
    noticia_gemela = noticia_fake.copy()
    noticia_gemela['fuente'] = "TestSource B" # Fuente distinta
    
    # IMPORTANTE: Para demostrar que la deduplicacion es por TITULO, 
    # cambiamos la URL (simulando que otro periodico linkea distinto).
    # Al cambiar URL, DEBE cambiar el hash (porque es hash de URL).
    new_url = f"http://test.com/noticia-{timestamp}-v2"
    noticia_gemela['url'] = new_url
    noticia_gemela['url_hash'] = hashlib.md5(new_url.encode('utf-8')).hexdigest()
    
    print(f"2. Insertando noticia GEMELA (Duplicada): '{noticia_gemela['titulo']}'...")
    print("   (El sistema deberia detectar el duplicado por TITULO y actualizar la ficha existente)")
    
    resultado = supabase_service.insert_news_deduplicacion([noticia_gemela])
    
    if resultado:
        print("\nPRUEBA COMPLETADA. Verificacion:")
        print("   - Revisa la tabla 'noticias' en Supabase.")
        print("   - Deberia existir 1 sola fila con ese titulo.")
        print("   - El campo 'fuente' deberia contener ambas fuentes concatenadas.")

    print("\n")
    print(" FIN DE LA PRUEBA")
    print("\n")

if __name__ == "__main__":
    ejecutar_prueba_base_datos()
