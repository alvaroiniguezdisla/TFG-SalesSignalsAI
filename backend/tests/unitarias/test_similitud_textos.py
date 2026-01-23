import sys
import os

# Fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.extraccion.manager import NewsExtractorManager

def prueba_deduplicacion_manual():
    manager = NewsExtractorManager()
    
    # 1. Definimos las noticias de prueba
    noticias_input = [
        {"titulo": "El Banco Santander sube un 5% en bolsa", "fuente": "Fuente A", "url": "url1"},
        {"titulo": "Banco Santander sube 5% en la bolsa", "fuente": "Fuente B", "url": "url2"},
        {"titulo": "El Real Madrid gana la liga", "fuente": "Fuente C", "url": "url3"}
    ]

    # 2. Mostramos INPUT
    print("\n--- 1. NOTICIAS ENTRANTES (INPUT) ---")
    for n in noticias_input:
        print(f"   [{n['fuente']}] {n['titulo']}")
    
    # 3. Llamamos a la función
    print("\n--- 2. PROCESO DE DEDUPLICACIÓN ---")
    print("(Buscando gemelos con >85% de parecido...)")
    resultado = manager.deduplicar_por_titulo(noticias_input)
    
    # 4. Mostramos OUTPUT
    print("\n--- 3. RESULTADO FINAL (OUTPUT) ---")
    for n in resultado:
        print(f"   [{n['fuente']}] {n['titulo']}")
        if 'urls_extra' in n:
            print(f"       Links guardados: {n['urls_extra']}")

    print("\n PRUEBA COMPLETADA")

if __name__ == '__main__':
    prueba_deduplicacion_manual()
