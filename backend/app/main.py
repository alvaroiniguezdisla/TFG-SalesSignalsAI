from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import noticias
from contextlib import asynccontextmanager
from app.core.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicio: Arrancar planificador
    print("Iniciando Scheduler...")
    start_scheduler()
    yield
    # Fin de ejecución
    print("Apagando servidor...")

app = FastAPI(
    title="SalesSignalsAI API",
    description="API para el Observatorio de Señales de Venta",
    version="1.0.0",
    lifespan=lifespan
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluimos routers
app.include_router(noticias.router)

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de SalesSignalsAI"}
