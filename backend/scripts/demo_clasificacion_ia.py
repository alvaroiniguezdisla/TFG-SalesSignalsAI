# ----------------------------------------------------------------------------------
# SCRIPT DE DEMOSTRACIÓN: CLASIFICACIÓN IA (PARA ENSEÑAR AL TRIBUNAL)
# Qué hace esto: Carga el modelo Llama 3.2 y le pasa dos noticias (una venta clara y otra ruido)
# Para qué sirve: Simplemente para enseñar en vivo cómo "piensa" la IA sin ejecutar todo el sistema.
# ----------------------------------------------------------------------------------

import sys
import os

# TRUCO: Añadimos la carpeta raíz al path para poder importar 'backend.app...'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.services.llm_clasificacion_noticias import LlmService

# Script manual para probar que la IA funciona bien
def probar_ia():
    print("Cargando Llama 3.2...")
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
        print(f"Relevancia: {res1['relevancia']}")
        print(f"Resumen: {res1['resumen_comercial']}")
    
    print("\n--- PRUEBA 2: RUIDO ---")
    res2 = ia.analizar_oportunidad(noticia_ruido["titulo"], noticia_ruido["contenido"])
    if res2:
        print(f"Relevancia: {res2['relevancia']}") # Deberia ser baja

if __name__ == "__main__":
    probar_ia()
