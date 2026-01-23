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
    #categoria_de_productos:pc,workstatios,impresoras,accesorios

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
        ACTÚA COMO: Un vendedor B2B Senior en HP (Hewlett-Packard).
        TU MISIÓN: Filtrar noticias basura y detectar OROPORTUNIDADES DE VENTA comercial (Nuevas oficinas, renovaciones tecnológicas, digitalización).

        Análisis Crítico:
        1. ¿Esta noticia implica que una empresa va a gastar dinero en tecnología?
           - SI -> Clasifica y puntúa alto.
           - NO (Política, Sucesos, Cotilleos, LeyOpinión) -> CATEGORÍA: "Sin Interés Comercial " (RUIDO).

        CATEGORÍAS PERMITIDAS (Elige SOLO una):
        - "Expansión / Crecimiento " -> Si abren sedes, contratan masivamente (Implica comprar PCs/Impresoras).
        - "Transformación Digital" -> Si modernizan sistemas, van a la nube, ciberseguridad.
        - "Resultados Financieros" -> SOLO si una empresa presenta beneficios récord (Tienen presupuesto).
        - "M&A / Fusiones" -> Fusiones de empresas (Reestructuración de IT).
        - "Sin Interés Comercial " -> TODO lo demás (Política, Deportes, Leyes generales, Sucesos).

        FORMATO DE RESPUESTA (JSON Estricto):
        - "categoria": Una de las opciones exactas de arriba.
        - "relevancia": 0 para RUIDO. 50-100 para oportunidades reales.
        - "resumen_comercial": Si es oportunidad, di QUÉ venderles (Laptops, Servidores, Impresoras). Si es RUIDO, di "Descartado por ser política/sucesos".
        - "empresas": Lista solo las empresas con potencial de compra. Si no hay, lista vacía [].

        IMPORTANTE: NO ALUCINES. Si es una noticia de Trump o de Gripe Aviar, ES RUIDO. No inventes conexiones.
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
            
            




