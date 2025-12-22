import ollama
import json
from enum import Enum
from pydantic import BaseModel, Field

# 1. Definimos las categorias que le importan a un comercila de HP
class SignalCategory(str, Enum):
    EXPANSION = "Expansión / Crecimiento " # Nuevas oficinas, empleo -> VENDER HARDWARE
    DIGITALIZACION ="Transformación Digital" # IA, Cloud, Ciber -> VENDER SOFTWARE/SERVICIOS
    RESULTADOS = "Resultados Financieros" # Beneficios récord -> TIENEN PRESUPUESTO
    FUSIONES = "M&A / Fusiones" # Cambios organizativos -> OPORTUNIDAD CONSULTORÍA
    RUIDO = "Sin Interés Comercial " # Política, Sucesos -> DESCARTAR

# 2. ESAQUEMA DE SALIDA (LO QUE VA A LA BASE DE DATOS)
class SalesSignal(BaseModel):
    categoria:  SignalCategory
    relevancia: int = Field(..., description="Puntuación 0-100 de interés para HP")
    resumen_comercial: str =Field(..., description="Justificación breve para el vendedor")
    empresas: list[str]= Field(..., description="Lista de empresas potenciales clientes")

# 3. EL SERVICIO DE IA
class LlmService:
    def __init__(self, modelo: str = "llama3.2"):
        self.modelo= modelo
    
    def analizar_oportunidad(self, titulo: str ,contenido: str ) ->dict:
        """
        Lee una noticia y extrae señales de venta para HP.
        """

        #PROMT (Instrucciones para el LLM)
        promt_sistema = """
        Eres un Director Comercial de HP (Hewlett-Packard). Buscas oportunidades B2B.
        
        Patrones de Venta:
        1. "Abre oficinas" / "Contrata gente" -> Categoría: EXPANSION.
        2. "Migra a la nube" / "Ciberseguridad" -> Categoría: DIGITALIZACION.
        3. Política, Deportes o Cotilleos -> Categoría: RUIDO (Relevancia 0).
        
        Responde SOLO con el JSON estricto.
        """

        promt_usuario = f"""
        Noticia: {titulo}
        Contenido: {contenido[:1000]}
        """

        try:
            #LLamada a Ollama
            respuesta= ollama.chat(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": promt_sistema},
                    {"role": "user", "content": promt_usuario}
                ],
                format=SalesSignal.model_json_schema()#Fuerza el formato JSON
            )

            #Devuelve el diccionario limpio
            return json.loads(respuesta['message']['content'])



        except Exception as e:
            print(f"Error en analizar noticia con LLM: {e}")
            return None
            
            




