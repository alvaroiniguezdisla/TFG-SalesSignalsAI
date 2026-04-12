# SalesSignalsAI

![Status](https://img.shields.io/badge/Status-TFG-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-19-blue?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.122-009688?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)

SalesSignalsAI es una plataforma de monitorizacion de noticias orientada a ventas B2B. El sistema extrae noticias desde RSS, scraping y navegador; las deduplica; las clasifica con IA; las guarda en Supabase; y permite consultarlas desde un dashboard web con autenticacion.

## Arquitectura

- Backend: FastAPI + Python
- Frontend: React + Vite
- Base de datos y autenticacion: Supabase
- IA local: Ollama
- Notificaciones: Microsoft Graph / Teams

## Requisitos previos

Antes de arrancar el proyecto, hacen falta estas piezas:

1. Node.js 20 o superior
2. Python 3.9 o superior
3. Docker Desktop, solo si se va a usar Docker
4. Ollama instalado de forma nativa, solo si se quiere ejecutar el pipeline de IA

### Ollama

Ollama no se ejecuta dentro de Docker. El backend, tanto en nativo como en Docker, espera encontrarlo en el host.

Instalacion y descarga del modelo:

```bash
ollama pull llama3.1
```

Comprobacion rapida:

```bash
ollama list
```

## Variables de entorno

El proyecto necesita dos archivos `.env`:

- `backend/.env`
- `frontend/.env`

En este repositorio se incluyen plantillas:

- `backend/.env.example`
- `frontend/.env.example`

Pasos recomendados:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Despues, rellena los valores reales de Supabase. Si no se van a probar las notificaciones de Teams, las variables `GRAPH_*` y `TEAMS_TARGET_USER_EMAIL` pueden dejarse vacias.

## Metodo 1: arranque clasico

Este es el recorrido mas transparente para una defensa de TFG porque deja claro que backend y frontend funcionan por separado.

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd ceu-salessignalsai
```

### 2. Levantar el backend

En una primera terminal:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Comprobacion:

- Abrir `http://localhost:8000`
- Debe responder: `{"message":"Bienvenido a la API de SalesSignalsAI"}`

### 3. Levantar el frontend

En una segunda terminal:

```bash
cd frontend
npm install
npm run dev
```

Comprobacion:

- Abrir `http://localhost:5173`
- Lo esperable al entrar por primera vez es la pantalla de login
- Ver la pantalla de login significa que el frontend esta funcionando correctamente

### 4. Como parar el arranque clasico

- En cada terminal, `Ctrl+C`
- Para salir del entorno virtual: `deactivate`

## Metodo 2: Docker

El proyecto tambien puede arrancarse entero con Docker Compose.

### Requisitos

- Docker Desktop abierto
- `backend/.env` y `frontend/.env` presentes
- Ollama instalado en el host si se quiere ejecutar la parte de IA

### Arranque

Desde la raiz del proyecto:

```bash
docker compose up --build -d
```

Alternativamente:

```bash
./start-docker.sh
```

Ese script usa internamente `docker compose` y limpia contenedores antiguos para evitar conflictos de puertos.

### Comprobacion

```bash
docker compose ps
```

Deben aparecer dos servicios `Up`:

- Backend en `http://localhost:8000`
- Frontend en `http://localhost:5173`

Comprobaciones visuales:

- `http://localhost:8000` debe devolver el JSON de bienvenida
- `http://localhost:5173` debe cargar la aplicacion
- Si sale login, no es un error: la ruta `/` esta protegida

### Logs

```bash
docker compose logs -f
```

### Parada

```bash
docker compose down
```

## Verificaciones rapidas para el tribunal

### Comprobacion minima sin usar IA

1. Configurar los `.env`
2. Levantar backend y frontend o `docker compose`
3. Entrar en `http://localhost:8000`
4. Entrar en `http://localhost:5173`
5. Ver que aparece la pantalla de login

Con eso queda demostrado que:

- el backend arranca
- el frontend arranca
- la aplicacion entrega la UI
- la API responde

### Comprobacion de IA

Para forzar una ejecucion manual del pipeline completo:

```bash
cd backend
source venv/bin/activate
python -m app.core.scheduler
```

Esto requiere:

- Supabase correctamente configurado
- Ollama corriendo en el host
- modelo `llama3.1` descargado

Si no se va a demostrar la parte de Teams, puede dejarse sin configurar.

## Testing

La bateria actual contiene:

- 33 tests unitarios
- 23 tests de integracion

### Ejecutar tests unitarios

```bash
cd backend
source venv/bin/activate
pytest tests/unitarios -q
```

### Ejecutar tests de integracion

```bash
cd backend
source venv/bin/activate
pytest tests/integracion -q
```

Los tests de integracion dependen de red y de servicios externos, por lo que son mas sensibles al entorno que los unitarios.

## Observaciones practicas

- El dashboard principal esta protegido por autenticacion; por eso la primera pantalla normal es el login.
- Si se usa Docker, no hace falta levantar backend y frontend a mano.
- Si ya hay algo ocupando `8000` o `5173`, hay que apagarlo antes de arrancar.
- Las notificaciones de Teams son opcionales para una demostracion basica.
- El proyecto no incluye las credenciales reales en el repositorio; deben entregarse aparte o rellenarse manualmente a partir de los `.env.example`.
