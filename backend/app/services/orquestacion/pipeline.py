from app.services.extraccion.manager import extractor
from bs4 import BeautifulSoup
from app.services.inteligencia import LlmService
from app.services.almacenamiento import SupabaseService

class NewsPipeline:
    def __init__(self):
        self.db = SupabaseService()
        self.llm= LlmService()

    def ejecutar(self):
        print("[PIPELINE] Iniciando proceso de ingesta y categorización de noticias...")

        #1. Hacemos ingesta de noticias 
        noticias_crudas= extractor.obtener_noticias()

        if not noticias_crudas:
            print("[PIPELINE] No se han podido obtener noticias")
            return
        
        print(f"[PIPELINE] Se han obtenido {len(noticias_crudas)} noticias")

        noticias_enriquecidas= []

        # 2. Analizamos una a una 
        for noticia in noticias_crudas:
            try:
                # Validacion de contenido: Intentar obtener texto para analizar
                raw_content = noticia.get('raw_content', '')
                
                if raw_content:
                    # --- LIMPIEZA DE TEXTO (si hay raw_content) ---
                    soup = BeautifulSoup(raw_content, 'html.parser')
                    texto_limpio = soup.get_text(separator=' ', strip=True)
                else:
                    # --- FALLBACK: usar título + resumen ---
                    titulo = noticia.get('titulo', '')
                    resumen = noticia.get('resumen', '')
                    texto_limpio = f"{titulo}. {resumen}".strip()
                    
                    if not texto_limpio or texto_limpio == ".":
                        print(f"[PIPELINE] Saltando noticia: sin contenido, título ni resumen disponible")
                        continue
                    
                    print(f"[PIPELINE] Usando fallback (título+resumen) para: {titulo[:40]}...")

                print(f"[PIPELINE] Analizando con IA: {noticia['titulo'][:50]}...") 
                
                # Llamada protegida a la IA
                analisis = self.llm.analizar_oportunidad(noticia['titulo'], texto_limpio)

                if analisis:
                    noticia['categoria_ia'] = analisis.get('categoria', 'Sin clasificar')
                    noticia['categoria_producto_ia'] = analisis.get('categoria_producto', 'Otros / No Aplica')
                    noticia['relevancia_ia'] = analisis.get('relevancia', 0)
                    noticia['resumen_comercial_ia'] = analisis.get('resumen_comercial', '')
                    noticia['empresas_clave_ia'] = analisis.get('empresas', [])
                else:
                    noticia['categoria_ia'] = "Error IA"
                    noticia['categoria_producto_ia'] = "Error IA"
                    noticia['relevancia_ia'] = 0
                    noticia['resumen_comercial_ia'] = "No se pudo analizar"
                    noticia['empresas_clave_ia'] = []

                noticias_enriquecidas.append(noticia)
            
            except Exception as e:
                print(f"[PIPELINE] Error procesando noticia '{noticia.get('titulo', 'Unknown')[:30]}': {e}")
                continue

        #4. Guardamos en la base de datos
        print("[PIPELINE] Guardando noticias en la base de datos...")
        
        self.db.insert_news_deduplicacion(noticias_enriquecidas)

        print(f"[PIPELINE] Se han guardado {len(noticias_enriquecidas)} noticias")


if __name__ == "__main__":
    pipeline = NewsPipeline()
    pipeline.ejecutar()