import sys
import os
from unittest.mock import patch

# Fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.extraccion.manager import extractor

def test_manager_browser_fallback_live():
    """
    Simula que RSS y Scraper están rotos.
    Verifica que el Manager salta al Browser (Playwright).
    """
    print("\n[TEST FALLBACK TOTAL] Simulando fallo de RSS y Scraper...")

    # Mockeamos RSS para que falle
    with patch('app.services.extraccion.manager.obtener_noticias_rss', return_value=[]) as mock_rss:
        # Mockeamos Scraper para que también falle
        with patch('app.services.extraccion.manager.scrape_noticias', return_value=[]) as mock_scraper:
            
            print("Iniciando extracción (esto puede tardar unos segundos porque abre el navegador)...")
            # Ejecutamos el Manager
            noticias = extractor.obtener_noticias()
            
            print(f"\nRSS 'saboteado' llamado {mock_rss.call_count} veces.")
            print(f"Scraper 'saboteado' llamado {mock_scraper.call_count} veces.")
            print(f"Total noticias rescatadas por Browser: {len(noticias)}")
            
            # Verificamos que tenemos datos
            if len(noticias) > 0:
                print("\n DETALLE DE NOTICIAS OBTENIDAS (MODO BROWSER):")
                noticias_por_fuente = {}
                for n in noticias:
                    f = n.get('fuente', 'Desconocida')
                    if f not in noticias_por_fuente:
                        noticias_por_fuente[f] = []
                    noticias_por_fuente[f].append(n['titulo'])
                
                for fuente, titulos in noticias_por_fuente.items():
                    print(f"\n   FUENTE: {fuente} ({len(titulos)})")
                    for i, titulo in enumerate(titulos):
                        print(f"     {i+1}. {titulo}")
            else:
                 print("\nFALLO: El Browser no recuperó nada. ¿Tienes Playwright instalado?")

if __name__ == "__main__":
    test_manager_browser_fallback_live()
