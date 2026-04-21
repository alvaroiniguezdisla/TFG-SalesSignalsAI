# ----------------------------------------------------------------------------------
# SCRIPT MANUAL: Demostracion de la clasificacion con IA
#
# Uso: python -m scripts.demo_clasificacion_ia
#
# Que hace: Envia dos noticias al LLM (Ollama) para verificar que la
# clasificacion funciona correctamente:
#   - Caso 1: Noticia con oportunidad de venta clara.
#   - Caso 2: Noticia irrelevante (ruido).
#
# Requisitos:
#   - Ollama instalado y funcionando (ollama serve)
#   - Modelo disponible en Ollama
#   - Configuracion `ollama_model` accesible desde la tabla `app_config`
#     (o modelo forzado manualmente al instanciar `LlmService`)
# ----------------------------------------------------------------------------------

from app.services.inteligencia.llm_clasificacion_noticias import LlmService


def mostrar_resultado(resultado):
    """Muestra los campos de clasificacion de forma legible."""
    if resultado:
        print(f"  Categoria negocio:  {resultado.get('categoria')}")
        print(f"  Producto HP:        {resultado.get('categoria_producto')}")
        print(f"  Relevancia:         {resultado.get('relevancia')}")
        print(f"  Resumen comercial:  {resultado.get('resumen_comercial')}")
        print(f"  Empresas:           {resultado.get('empresas')}")
    else:
        print("  Error: La IA no devolvio resultado.")


def ejecutar():
    print("Cargando modelo de IA...")
    ia = LlmService()

    casos = [
        {
            "nombre": "CASO 1: Oportunidad de venta (Glovo)",
            "titulo": "Glovo anuncia la apertura de un nuevo Hub tecnologico en Barcelona "
                    "y contratara a 400 ingenieros",
            "contenido": "La empresa de delivery sigue expandiendose y busca talento tech..."
        },
        {
            "nombre": "CASO 2: Ruido (Gobierno)",
            "titulo": "El gobierno aprueba la nueva ley de educacion",
            "contenido": "El ministro ha declarado que la reforma sera estructural..."
        }
    ]

    for caso in casos:
        print(f"\n--- {caso['nombre']} ---")
        resultado = ia.analizar_oportunidad(caso["titulo"], caso["contenido"])
        mostrar_resultado(resultado)


if __name__ == "__main__":
    ejecutar()
