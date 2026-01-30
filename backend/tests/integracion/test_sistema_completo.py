import sys
import os
import time

# Fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.orquestacion.pipeline import NewsPipeline

def ejecutar_pipeline_real():
    print("\n")
    print("==================================================================")
    print(" INICIO DEL PIPELINE REAL (SIN MOCKS)")
    print("==================================================================")
    print("Este script ejecutara el pipeline de produccion completo:")
    print("1. INGESTA: Descarga noticias de RSS/Web (El Pais, El Economista).")
    print("2. MATRICIAL (IA): Analiza cada noticia con Ollama (llama3.2).")
    print("3. STORAGE: Guarda en Supabase (con Deduplicacion Inteligente).")
    print("\n")
    print("Requisitos:")
    print(" - 'ollama serve' corriendo.")
    print(" - Internet activo.")
    print(" - Credenciales Supabase en .env.")
    print("\n")

    start_time = time.time()
    
    try:
        pipeline = NewsPipeline()
        pipeline.ejecutar()
        
    except Exception as e:
        print(f"\nERROR CRITICO: {e}")
        # Si es error de importacion de ollama, damos pista
        if "No module named 'ollama'" in str(e):
             print("\n[PISTA] Parece que falta la libreria 'ollama'. Ejecuta: pip install ollama")

    end_time = time.time()
    duration = end_time - start_time
    
    print("\n")
    print("==================================================================")
    print(f"FIN DEL PROCESO (Tiempo total: {duration:.2f}s)")
    print("==================================================================")
    print("\n")

if __name__ == "__main__":
    ejecutar_pipeline_real()
