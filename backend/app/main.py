from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import noticias, admin
from contextlib import asynccontextmanager
from app.core.scheduler import start_scheduler
from app.core.config import settings

import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicio: Arrancar planificador
    logger.info("Iniciando Scheduler...")
    start_scheduler()
    yield
    # Fin de ejecución
    logger.info("Apagando servidor...")

app = FastAPI(
    title="SalesSignalsAI API",
    description="API para el Observatorio de Señales de Venta",
    version="1.0.0",
    lifespan=lifespan
)

# Configuración CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluimos routers
app.include_router(noticias.router)
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de SalesSignalsAI"}
