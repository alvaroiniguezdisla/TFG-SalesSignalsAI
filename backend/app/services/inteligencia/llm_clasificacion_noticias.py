import ollama
import json
from enum import Enum
from pydantic import BaseModel, Field
from app.core.config import settings

# 1. CATEGORÍAS DE PRODUCTO HP 
class ProductCategory(str, Enum):
    GAMING = "Gaming / OMEN"
    IMPRESION = "Impresión y Escáner"
    CONSUMO = "PC Consumo (Hogar/Estudiantes)"
    EMPRESAS = "Soluciones Empresariales (ProBook/Elite)"
    SERVICIOS = "Servicios y Soluciones IT"
    OTROS = "Otros / No Aplica"

# 2. SEÑALES DE NEGOCIO 
class SignalCategory(str, Enum):
    EXPANSION = "Expansión / Crecimiento " # Nuevas oficinas, empleo -> VENDER HARDWARE
    DIGITALIZACION ="Transformación Digital" # IA, Cloud, Ciber -> VENDER SOFTWARE/SERVICIOS
    RESULTADOS = "Resultados Financieros" # Beneficios récord -> TIENEN PRESUPUESTO
    FUSIONES = "M&A / Fusiones" # Cambios organizativos -> OPORTUNIDAD CONSULTORÍA
    RUIDO = "Sin Interés Comercial " # Política, Sucesos -> DESCARTAR

# 3. ESQUEMA DE SALIDA 
class SalesSignal(BaseModel):
    categoria: SignalCategory = Field(..., description="Categoría de negocio a la que pertenece la noticia")
    categoria_producto: ProductCategory = Field(..., description="Línea de producto HP más adecuada para vender aquí")
    relevancia: int = Field(..., description="Puntuación 0-100 de interés para HP")
    resumen_comercial: str = Field(..., description="Justificación breve para el vendedor")
    empresas: list[str] = Field(..., description="Lista de empresas potenciales clientes")

# 4. EL SERVICIO DE IA
class LlmService:
    def __init__(self, modelo: str = settings.OLLAMA_MODEL):
        self.modelo= modelo
    
    def analizar_oportunidad(self, titulo: str ,contenido: str ) ->dict:
        """
        Lee una noticia y extrae señales de venta para HP.
        """

        #PROMT (Instrucciones para el LLM)
        promt_sistema = """
        ACTÚA COMO: Un experto en ventas B2B de HP (Hewlett-Packard).
        TU OBJETIVO: Analizar noticias para detectar oportunidades de venta de productos HP.

        PASO 1: DETECTAR LA SEÑAL DE NEGOCIO
        - Expansión / Crecimiento: ¿Abren oficinas? (Oportunidad de vender PCs e Impresoras masivamente).
        - Transformación Digital: ¿Modernizan tecnología? (Oportunidad de servicios y portátiles de alta gama).
        - Resultados Financieros: ¿Ganan mucho dinero? (Tienen presupuesto).
        - M&A / Fusiones: ¿Se unen empresas? (Renovación de flotas de equipos).
        - Sin Interés Comercial: Política, leyes, cotilleos, sucesos. (RUIDO).

        PASO 2: ASIGNAR PRODUCTO HP (¿QUÉ LES VENDEMOS?)
        - "Gaming / OMEN": Si hablan de eSports, videojuegos, diseño gráfico potente.
        - "Impresión y Escáner": Si abren oficinas físicas, gestión documental.
        - "PC Consumo (Hogar/Estudiantes)": Si es para usuarios finales, educación, vuelta al cole.
        - "Soluciones Empresariales (ProBook/Elite)": Si son empresas comprando portátiles para empleados.
        - "Servicios y Soluciones IT": Ciberseguridad, nube, gestión de flotas.
        - "Otros / No Aplica": Si es Ruido o no encaja claro.

        FORMATO RESPUESTA (JSON):
        Devuelve un JSON exacto con los campos: "categoria", "categoria_producto", "relevancia" (0-100), "resumen_comercial" (explica qué producto vender y por qué) y "empresas" (quién compra).
        
        EJEMPLO DE RAZONAMIENTO:
        "Empresa X abre nueva sede en Madrid" -> Expansión -> Necesitan PCs para empleados -> "Soluciones Empresariales".
        "Torneo de LoL patrocinado por X" -> Marketing -> "Gaming / OMEN".
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
            
            




