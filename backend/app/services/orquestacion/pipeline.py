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
            # --- LIMPIEZA DE TEXTO (MEJORADO) ---
            soup = BeautifulSoup(noticia.get('raw_content', ''), 'html.parser')
            texto_limpio = soup.get_text(separator=' ', strip=True)
            print(f" [IA] Texto limpio enviado: {texto_limpio[:100]}...") 

            analisis = self.llm.analizar_oportunidad(noticia['titulo'], texto_limpio)

            # --- AÑADE ESTO ---
            if analisis:
                print(f" DEBUG IA RAW: {analisis}")
            # ------------------

            if analisis:
                #3. Guardamos en la base de datos
                
                noticia['categoria_ia']= analisis['categoria']
                noticia['relevancia_ia'] = analisis['relevancia']
                noticia['resumen_comercial_ia'] = analisis['resumen_comercial']
                noticia['empresas_clave_ia'] = analisis['empresas']

            else:
                # Fallback por si la IA no funciona
                noticia['categoria_ia'] = "Error IA"
                noticia['relevancia_ia'] = 0
                noticia['resumen_comercial_ia'] = "Falló el análisis"
                noticia['empresas_clave_ia'] = []

            noticias_enriquecidas.append(noticia)

        #4. Guardamos en la base de datos
        print("[PIPELINE] Guardando noticias en la base de datos...")
        
        self.db.insert_news(noticias_enriquecidas)

        print(f"[PIPELINE] Se han guardado {len(noticias_enriquecidas)} noticias")


if __name__ == "__main__":
    pipeline = NewsPipeline()
    pipeline.ejecutar()