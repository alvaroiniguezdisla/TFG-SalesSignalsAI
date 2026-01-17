import sys
import os

# Truco para encontrar la carpeta 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.extraccion.scraper import scrape_elpais_portada
from app.services.almacenamiento.database import SupabaseService

def ejecutar_prueba():
    print("Iniciando prueba de pipeline...")
    
    #1. Scrapeamos
    print("Lanzando Scraper...")
    noticias = scrape_elpais_portada()
    
    if not noticias:
        print("El scraper no devolvió nada. Revisa tu conexión o el scraper.")
        return

    print(f"Scraper OK: Se encontraron {len(noticias)} noticias.")

    #2. Guardamos
    print("Intentando guardar en Supabase...")
    db = SupabaseService()
    resultado = db.insert_news(noticias)
    
    if resultado:
        print("ÉXITO ! Las noticias deberían estar en tu tabla 'noticias'.")
    else:
        print("Hubo un problema al guardar (o ya existían todas).")

if __name__ == "__main__":
    ejecutar_prueba()
