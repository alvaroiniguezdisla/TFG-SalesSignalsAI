import ollama
import json
from enum import Enum
from pydantic import BaseModel, Field
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
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

# 3. MODELO DE EMPRESA ENRIQUECIDA
class EmpresaDetectada(BaseModel):
    nombre: str = Field(..., description="Nombre de la empresa detectada")
    tamano: str = Field(default="Desconocido", description="Startup, PYME, Mediana Empresa, Gran Cuenta o Desconocido")

# 4. ESQUEMA DE SALIDA
class SalesSignal(BaseModel):
    categoria: SignalCategory = Field(..., description="Categoría de negocio a la que pertenece la noticia")
    categoria_producto: ProductCategory = Field(..., description="Línea de producto HP más adecuada para vender aquí")
    relevancia: int = Field(..., description="Puntuación 0-100 de interés para HP")
    resumen_comercial: str = Field(..., description="Resumen para el vendedor: qué vender, por qué, y contexto corporativo")
    empresas: list[EmpresaDetectada] = Field(..., description="Empresas detectadas con su clasificación de tamaño")
    talk_track: str = Field(default="", description="3-4 puntos clave para que el comercial inicie una conversación")
    email_draft: str = Field(default="", description="Borrador de email profesional de primer contacto")

# 5. EL SERVICIO DE IA
class LlmService:
    def __init__(self, modelo: str = settings.OLLAMA_MODEL):
        self.modelo= modelo
    
    def analizar_oportunidad(self, titulo: str ,contenido: str ) ->dict:
        """
        Lee una noticia y extrae señales de venta para HP.
        """

        promt_sistema = """
        ACTUA COMO: Un analista senior de ventas B2B de HP (Hewlett-Packard) con 15 años de experiencia.
        TU OBJETIVO: Analizar una noticia y generar inteligencia comercial accionable para el equipo de ventas.

        PASO 1: DETECTAR LA SENAL DE NEGOCIO
        Clasifica la noticia en UNA de estas categorias:
        - "Expansión / Crecimiento ": Abren oficinas, contratan, se expanden -> VENDER HARDWARE MASIVO.
        - "Transformación Digital": Modernizan tecnología, IA, Cloud, Ciber -> VENDER SERVICIOS/SOFTWARE.
        - "Resultados Financieros": Buenos resultados economicos -> TIENEN PRESUPUESTO.
        - "M&A / Fusiones": Fusiones, adquisiciones, cambios organizativos -> RENOVACION DE FLOTAS.
        - "Sin Interés Comercial ": Politica, leyes, sucesos, cotilleos -> RUIDO, DESCARTAR.

        PASO 2: ASIGNAR PRODUCTO HP
        Elige la linea de producto MAS adecuada:
        - "Gaming / OMEN": eSports, videojuegos, diseño gráfico.
        - "Impresión y Escáner": Oficinas fisicas, gestion documental, logistica.
        - "PC Consumo (Hogar/Estudiantes)": Usuarios finales, educación.
        - "Soluciones Empresariales (ProBook/Elite)": Portatiles y PCs corporativos para empleados.
        - "Servicios y Soluciones IT": Ciberseguridad, nube, gestion de flotas IT.
        - "Otros / No Aplica": Si es ruido o no encaja.

        PASO 3: IDENTIFICAR EMPRESAS Y CLASIFICAR SU TAMANO
        Detecta las empresas mencionadas en la noticia (maximo 3). Para cada una, clasifica su tamano:
        - "Startup": Menos de 50 empleados, rondas de financiacion, recien creada.
        - "PYME": Entre 50 y 250 empleados, ambito local o regional.
        - "Mediana Empresa": Entre 250 y 1000 empleados, presencia nacional.
        - "Gran Cuenta": Mas de 1000 empleados, multinacionales, cotizadas en bolsa (Ej: Telefonica, BBVA, Repsol, Inditex).
        - "Desconocido": Si no hay datos suficientes.

        PASO 4: RESUMEN COMERCIAL (resumen_comercial)
        Escribe un resumen de 3-5 frases para el vendedor que incluya:
        1. Que esta ocurriendo en la noticia.
        2. Por que es relevante para HP (oportunidad concreta).
        3. Que producto o servicio HP encaja y por que.

        PASO 5: ARGUMENTARIO COMERCIAL (talk_track)
        Genera exactamente 3-4 puntos que el comercial puede usar al llamar al cliente.
        Cada punto en una linea nueva, empezando con un guion "-".
        Ejemplo:
        - Felicitar por la expansion y preguntar por sus necesidades tecnologicas.
        - Presentar HP Elite como solucion para entornos corporativos con gestion centralizada.
        - Mencionar HP Device as a Service (DaaS) para optimizar costes.
        - Proponer una demo personalizada en sus oficinas.

        PASO 6: BORRADOR DE EMAIL (email_draft)
        Escribe un email profesional de primer contacto (maximo 150 palabras).
        Requisitos:
        - Hacer referencia indirecta a la noticia (sin parecer invasivo).
        - Proponer una reunion o llamada breve.
        - Tono: cordial, directo y profesional.
        - Incluir un "Asunto:" al inicio.

        FORMATO DE RESPUESTA:
        Devuelve un JSON con estos campos exactos:
        - "categoria": una de las categorias del Paso 1
        - "categoria_producto": una de las lineas del Paso 2
        - "relevancia": numero entero de 0 a 100
        - "resumen_comercial": texto del Paso 4
        - "empresas": lista de objetos con "nombre" y "tamano" (Paso 3)
        - "talk_track": texto con los puntos del Paso 5
        - "email_draft": texto completo del email del Paso 6

        EJEMPLO DE RAZONAMIENTO:
        "Telefonica abre 15 nuevas oficinas en España"
        -> Expansion -> Necesitan PCs, impresoras, monitores -> "Soluciones Empresariales"
        -> empresas: [{"nombre": "Telefonica", "tamano": "Gran Cuenta"}]
        -> relevancia: 85
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
            logger.error(f"Error en analizar noticia con LLM: {e}")
            return None
            
            




