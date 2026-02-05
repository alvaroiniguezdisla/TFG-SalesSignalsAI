# Script de prueba para validar la clasificación de noticias con el LLM.
# Carga el modelo y prueba dos casos (éxito y ruido) para verificar la salida JSON.

import sys
import os

# Añadimos la carpeta raíz al path para poder importar 'backend.app...'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.inteligencia.llm_clasificacion_noticias import LlmService

# Función principal de prueba
def probar_ia():
    print("Cargando Llama 3.1...")
    ia = LlmService()
    
    # Caso 1: Venta clara
    noticia_venta = {
        "titulo": "Glovo anuncia la apertura de un nuevo Hub tecnológico en Barcelona y contratará a 400 ingenieros",
        "contenido": "La empresa de delivery sigue expandiéndose y busca talento tech..."
    }
    
    # Caso 2: Nada que ver
    noticia_ruido = {
        "titulo": "El gobierno aprueba la nueva ley de educación",
        "contenido": "El ministro ha declarado que la reforma será estructural..."
    }

    print("\n--- PRUEBA 1: VENTA (Glovo) ---")
    res1 = ia.analizar_oportunidad(noticia_venta["titulo"], noticia_venta["contenido"])
    if res1:
        print(f"Categoría Negocio: {res1.get('categoria')}")
        print(f"Producto HP: {res1.get('categoria_producto')}")
        print(f"Relevancia: {res1.get('relevancia')}")
        print(f"Resumen: {res1.get('resumen_comercial')}")
        print(f"Empresas: {res1.get('empresas')}")
    
    print("\n--- PRUEBA 2: RUIDO ---")
    res2 = ia.analizar_oportunidad(noticia_ruido["titulo"], noticia_ruido["contenido"])
    if res2:
        print(f"Categoría Negocio: {res2.get('categoria')}")
        print(f"Producto HP: {res2.get('categoria_producto')}")
        print(f"Relevancia: {res2.get('relevancia')}")
        print(f"Resumen: {res2.get('resumen_comercial')}")
        print(f"Empresas: {res2.get('empresas')}")

if __name__ == "__main__":
    probar_ia()
