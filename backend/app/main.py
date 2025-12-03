from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import noticias

app = FastAPI(
    title="SalesSignalsAI API",
    description="API para el Observatorio de Señales de Venta",
    version="1.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(noticias.router)

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de SalesSignalsAI"}
