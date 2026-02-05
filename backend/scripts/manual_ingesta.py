# Script para ejecutar la ingesta de noticias manualmente.
# Útil para depurar conectores y verificar que las fuentes responden correctamente.

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.extraccion.manager import extractor

def proba_ingesta():
    print("\n")
    print(" INICIO PRUEBA DE INGESTA REAL (SIN MOCKS)")
    print("\n")

    print("Conectando con fuentes configuradas...")
    
    try:
        noticias = extractor.obtener_noticias()
        print(f"\nRESULTADO: Se han obtenido {len(noticias)} noticias.")
        
        if noticias:
            print("\n")
            print(f" DETALLE DE LAS PRIMERAS {min(5, len(noticias))} NOTICIAS:")
            print("\n")
            
            for i, noticia in enumerate(noticias[:5]):
                print(f"\n[NOTICIA #{i+1}]")
                # Imprimimos todos los campos de forma ordenada
                for clave, valor in noticia.items():
                    # Si el contenido es muy largo (como raw_content), lo recortamos para visualizar
                    valor_str = str(valor)
                    if len(valor_str) > 100:
                        valor_str = valor_str[:97] + "..."
                    print(f"   - {clave}: {valor_str}")
                print("   -----------------------")

    except Exception as e:
        print(f"\nERROR DURANTE LA INGESTA: {e}")

    print("\n")
    print(" FIN DE LA PRUEBA")
    print("\n")

if __name__ == "__main__":
    proba_ingesta()
