import sys
import os
import time
import json
from unittest.mock import MagicMock

# ---------------------------------------------------------
# MOCK DE OLLAMA (Para entorno de pruebas sin servicio activo)
# ---------------------------------------------------------
mock_ollama = MagicMock()
mock_response = {
    'message': {
        'content': json.dumps({
            "categoria": "Expansión / Crecimiento ",
            "relevancia": 85,
            "resumen_comercial": "TechCorp invertira 5M en servidores. Oportunidad para vender Hardware.",
            "empresas": ["TechCorp"]
        })
    }
}
mock_ollama.chat.return_value = mock_response
sys.modules["ollama"] = mock_ollama
# ---------------------------------------------------------

# Fix path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.inteligencia.llm_clasificacion_noticias import LlmService

def ejecutar_prueba_ia():
    print("\n")
    print(" INICIO DE PRUEBA: INTELIGENCIA ARTIFICIAL (MOCK)")
    print("\n")
    print("Objetivo: Comprobar comunicacion y formateo JSON del servicio LlmService.")
    print("Modelo Configurado: llama3.2")
    
    # 1. Creamos noticia de ejemplo
    titulo = "La empresa TechCorp subre un ciberataque masivo y planea renovar toda su infraestructura."
    contenido = "Tras el incidente de ransomware, el CEO ha anunciado una inversión de 5 millones en nuevos servidores y firewalls de última generación. Buscan proveedores urgentes."
    
    print(f"\n[INPUT] Enviando noticia a la IA...")
    print(f"   - Título: {titulo}")
    
    try:
        # 2. Instanciamos el servicio
        llm = LlmService(modelo="llama3.2")
        start = time.time()
        
        # 3. Llamamos a la API
        resultado = llm.analizar_oportunidad(titulo, contenido)
        
        duration = time.time() - start
        
        if resultado:
            print(f"\nPROCESO COMPLETADO (Tiempo: {duration:.2f}s)")
            print("\n")
            print(" RESPUESTA DEL LLM:")
            print("\n")
            for k, v in resultado.items():
                print(f"   - {k}: {v}")
            
            # Validación simple
            if resultado.get('relevancia', 0) > 70:
                print("\nDIAGNOSTICO: La IA ha detectado correctamente la oportunidad.")
            else:
                print("\nDIAGNOSTICO: La IA no ha considerado relevante la noticia.")
                
        else:
            print("\nERROR: La IA devolvió una respuesta vacía.")

    except Exception as e:
        print(f"\nEXCEPCION: {e}")

    print("\n")
    print(" FIN DE LA PRUEBA")
    print("\n")

if __name__ == "__main__":
    ejecutar_prueba_ia()
