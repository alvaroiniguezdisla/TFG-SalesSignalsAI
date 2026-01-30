import sys
import os

# TRUCO: Añadimos la carpeta raíz al path para poder importar 'backend.app...'
# Esto permite ejecutar el script desde la raíz del proyecto o desde cualquier subcarpeta.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.services.llm_clasificacion_noticias import LlmService

def test_ia_comercial():
    print("🧠 Cargando modelo Llama 3.2 (Simulando Director Comercial HP)...")
    ia = LlmService()
    
    # CASO 1: OPORTUNIDAD CLARA (Venta de Portátiles)
    noticia_expansion = {
        "titulo": "Glovo anuncia la apertura de un nuevo Hub tecnológico en Barcelona y contratará a 400 ingenieros",
        "contenido": "La empresa de delivery sigue expandiéndose y busca talento tech para su nueva sede. Se espera que el centro esté operativo en 2025..."
    }
    
    # CASO 2: RUIDO (Política/Sin Venta)
    noticia_ruido = {
        "titulo": "El gobierno aprueba la nueva ley de educación en el congreso",
        "contenido": "El ministro ha declarado que la reforma será estructural y afectará a primaria y secundaria..."
    }

    print("\n---------------------------------------------------")
    print("🟢 PRUEBA 1: Expansión (Debería detectar VENTA)")
    print(f"Noticia: {noticia_expansion['titulo']}")
    print("... Analizando ...")
    
    resultado1 = ia.analizar_oportunidad(noticia_expansion["titulo"], noticia_expansion["contenido"])
    
    if resultad1:
        print(f"📂 Categoría: {resultado1['categoria']}")
        print(f"📊 Relevancia: {resultado1['relevancia']}/100")
        print(f"💡 Consejo Comercial: {resultado1['resumen_comercial']}")
    else:
        print("❌ Error: La IA no devolvió nada.")

    print("\n---------------------------------------------------")
    print("🔴 PRUEBA 2: Ruido (Debería dar RELEVANCIA BAJA)")
    print(f"Noticia: {noticia_ruido['titulo']}")
    print("... Analizando ...")
    
    resultado2 = ia.analizar_oportunidad(noticia_ruido["titulo"], noticia_ruido["contenido"])
    
    if resultado2:
        print(f"📂 Categoría: {resultado2['categoria']}")
        print(f"📊 Relevancia: {resultado2['relevancia']}/100")
    else:
        print("❌ Error: La IA no devolvió nada.")

if __name__ == "__main__":
    test_ia_comercial()
