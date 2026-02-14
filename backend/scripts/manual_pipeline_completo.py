# ----------------------------------------------------------------------------------
# SCRIPT MANUAL: Ejecucion del pipeline completo
#
# Uso: python -m scripts.manual_pipeline_completo
#
# Que hace: Ejecuta el proceso completo de produccion:
#   1. INGESTA:  Descarga noticias de RSS, Scraper o Browser.
#   2. IA:       Analiza cada noticia con Ollama (clasificacion + relevancia).
#   3. STORAGE:  Guarda en Supabase con deduplicacion inteligente.
#
# Requisitos:
#   - Ollama instalado y funcionando (ollama serve)
#   - Internet activo
#   - Credenciales Supabase en .env
# ----------------------------------------------------------------------------------

import time
from app.services.orquestacion.pipeline import NewsPipeline


def ejecutar():
    print("=" * 60)
    print("Ejecutando pipeline completo (Ingesta -> IA -> Base de datos)")
    print("=" * 60)

    start_time = time.time()

    try:
        pipeline = NewsPipeline()
        pipeline.ejecutar()

    except Exception as e:
        print(f"\nError critico: {e}")
        if "No module named 'ollama'" in str(e):
            print("Solucion: pip install ollama")

    duration = time.time() - start_time

    print("=" * 60)
    print(f"Proceso finalizado (Tiempo total: {duration:.2f}s)")
    print("=" * 60)


if __name__ == "__main__":
    ejecutar()
