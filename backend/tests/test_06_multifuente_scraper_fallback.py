import sys
import os
from unittest.mock import patch

# Fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.extraccion.manager import extractor

def test_manager_scraper_fallback_live():
    """
    Simula que el RSS está roto para TODAS las fuentes.
    Verifica que el Manager salta al Scraper y obtiene noticias reales.
    """
    print("\n[TEST FALLBACK] Simulando fallo masivo de RSS...")

    # Forzamos error en RSS para que el manager active el plan B (Scraper)
    with patch('app.services.extraccion.manager.obtener_noticias_rss', return_value=[]) as mock_rss:
        
        # Ejecutamos el Manager normal
        noticias = extractor.obtener_noticias()
        
        print(f"\nRSS 'saboteado' llamado {mock_rss.call_count} veces (una por fuente).")
        print(f"Total noticias rescatadas por Scraper: {len(noticias)}")
        
        # Agrupamos para validar
        por_fuente = {}
        for n in noticias:
            f = n.get('fuente', 'Desconocida')
            por_fuente[f] = por_fuente.get(f, 0) + 1
            
        for fuente, count in por_fuente.items():
            print(f"   - {fuente}: {count} noticias")
            
        if len(noticias) > 0:
            print("\n DETALLE DE NOTICIAS OBTENIDAS (MODO SCRAPER):")
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
            print("\nFALLO: El Scraper no recuperó nada. El fallback falló.")

if __name__ == "__main__":
    test_manager_scraper_fallback_live()
