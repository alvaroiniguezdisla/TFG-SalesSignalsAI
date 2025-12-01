from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scraper  import obtener_noticias


app =FastAPI()

#Configuramos el middleware CORS para dejar pasar al frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Definimos la ruta raiz
@app.get("/")
def read_root():
    return {"mensaje": "El backend está funcionando "}


#Definimos la ruta de noticias

@app.get("/noticias")
def get_noticias():
    #LLamamos a nuestro robot scraper para que busque las noticias
    noticias =obtener_noticias()
    return noticias
