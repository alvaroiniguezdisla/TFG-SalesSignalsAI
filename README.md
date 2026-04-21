# SalesSignalsAI

![Status](https://img.shields.io/badge/Status-TFG-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-19-blue?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.122-009688?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)

Plataforma de monitorización de noticias para ventas B2B. Extrae noticias de fuentes RSS y scraping, las deduplica, las clasifica con IA (Ollama + LLaMA 3.1), las almacena en Supabase y las muestra en un dashboard web con autenticación.

## Arquitectura

| Componente                     | Tecnología                      |
| ------------------------------ | -------------------------------- |
| Backend (API)                  | FastAPI + Python                 |
| Frontend (interfaz web)        | React + Vite                     |
| Base de datos y autenticación | Supabase (PostgreSQL en la nube) |
| IA local                       | Ollama con modelo LLaMA 3.1      |
| Notificaciones                 | Microsoft Graph / Teams          |

## Estructura del proyecto

```
ceu-salessignalsai/
├── backend/               # API REST (FastAPI)
│   ├── app/               # Código fuente del backend
│   │   ├── api/           # Endpoints de la API
│   │   ├── core/          # Configuración y scheduler
│   │   ├── schemas/       # Modelos de datos (Pydantic)
│   │   └── services/      # Lógica de negocio (extracción, IA, almacenamiento, notificaciones)
│   ├── scripts/           # Utilidades manuales de apoyo y demostración
│   ├── tests/             # Tests unitarios y de integración
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/              # Interfaz web (React)
│   ├── src/
│   │   ├── pages/         # Páginas (Login, Dashboard, Admin, etc.)
│   │   ├── components/    # Componentes reutilizables
│   │   └── hooks/         # Hooks personalizados
│   └── Dockerfile
├── docker-compose.yml     # Orquestación de contenedores
└── README.md
```

## Requisitos previos

Para ejecutar el proyecto hace falta:

1. **Node.js 20** o superior — [Descargar aquí](https://nodejs.org/)
2. **Python 3.9** o superior — [Descargar aquí](https://www.python.org/downloads/)
3. **Docker Desktop** (solo para el método Docker) — [Descargar aquí](https://www.docker.com/products/docker-desktop/)
4. **Ollama** (solo si se quiere probar el pipeline de IA) — [Descargar aquí](https://ollama.com/)

### Ollama

Ollama se ejecuta fuera de Docker, directamente en el sistema operativo. Si se quiere probar la clasificación con IA, hay que instalarlo y descargar el modelo:

```bash
ollama pull llama3.1
```

Para comprobar que se ha descargado correctamente:

```bash
ollama list
```

> **Nota:** Si solo se quiere comprobar que la aplicación web arranca (backend + frontend), Ollama no es necesario.

## Configuración de las variables de entorno

El proyecto necesita dos archivos `.env` con las credenciales de Supabase. Se incluyen plantillas de ejemplo en el repositorio.

### Paso 1: copiar las plantillas

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

En Windows (PowerShell):

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
```

### Paso 2: rellenar los valores

Las credenciales reales de Supabase se entregan junto con la memoria del TFG en un documento aparte. Hay que copiarlas en los archivos `.env` creados en el paso anterior.

**`backend/.env`** — Variables del backend:

| Variable                      | Descripción                                             |
| ----------------------------- | -------------------------------------------------------- |
| `SUPABASE_URL`              | URL del proyecto en Supabase (se proporciona)            |
| `SUPABASE_KEY`              | Clave anon/service de Supabase (se proporciona)          |
| `SUPABASE_SERVICE_ROLE_KEY` | Clave de servicio con permisos elevados (se proporciona) |
| `GRAPH_TENANT_ID`           | Tenant de Azure para Teams (opcional)                    |
| `GRAPH_CLIENT_ID`           | Client ID de Azure para Teams (opcional)                 |
| `GRAPH_SCOPES`              | Permisos de Microsoft Graph (opcional)                   |
| `TEAMS_TARGET_USER_EMAIL`   | Email del destinatario de Teams (opcional)               |

**`frontend/.env`** — Variables del frontend:

| Variable                   | Descripción                                           |
| -------------------------- | ------------------------------------------------------ |
| `VITE_API_URL`           | URL del backend, por defecto `http://localhost:8000` |
| `VITE_SUPABASE_URL`      | URL del proyecto en Supabase (se proporciona)          |
| `VITE_SUPABASE_ANON_KEY` | Clave pública (anon) de Supabase (se proporciona)     |

> Las variables marcadas como "opcional" son para las notificaciones de Teams y se pueden dejar vacías sin afectar al funcionamiento general.

## Credenciales de acceso a la aplicación

Una vez arrancada la aplicación, la pantalla inicial es un login. El acceso real se hace con **correo electrónico y contraseña**, no con un alias corto de usuario.

Las credenciales exactas de la cuenta de prueba se entregan junto con el TFG. Al iniciar sesión hay que introducir el **correo completo** de esa cuenta.

| Campo       | Valor       |
| ----------- | ----------- |
| Correo electrónico | Cuenta de prueba entregada junto con el TFG |
| Contraseña | Contraseña entregada junto con el TFG |

## Método 1: arranque en local (sin Docker)

Este método levanta backend y frontend por separado, cada uno en su propia terminal.

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd ceu-salessignalsai
```

### 2. Backend

Abrir una terminal y ejecutar:

```bash
cd backend
python -m venv venv
source venv/bin/activate        # En macOS / Linux
# venv\Scripts\activate          # En Windows (PowerShell)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

> Este arranque inicia también el scheduler en segundo plano dentro del backend.

Para comprobar que funciona, abrir en el navegador `http://localhost:8000`. Debería devolver:

```json
{"message": "Bienvenido a la API de SalesSignalsAI"}
```

### 3. Frontend

Abrir otra terminal y ejecutar:

```bash
cd frontend
npm install
npm run dev
```

Abrir en el navegador `http://localhost:5173`. Debería aparecer la pantalla de login.

### 4. Para parar

- Pulsar `Ctrl+C` en cada terminal
- Escribir `deactivate` en la terminal del backend para salir del entorno virtual

## Método 2: Docker Compose

Levanta todo (backend + frontend) con un solo comando. No hace falta instalar dependencias manualmente.

### Requisitos

- Docker Desktop abierto
- Archivos `.env` configurados (ver sección anterior)

### Arranque

Desde la carpeta raíz del proyecto:

```bash
docker compose up --build -d
```

### Comprobar que funciona

```bash
docker compose ps
```

Deberían aparecer dos servicios en estado `Up`:

- Backend → `http://localhost:8000`
- Frontend → `http://localhost:5173`

### Ver logs

```bash
docker compose logs -f
```

### Parar

```bash
docker compose down
```

## Guía rápida de verificación para el tribunal

### Verificación básica (sin IA)

1. Configurar los archivos `.env` con las credenciales proporcionadas
2. Levantar la aplicación (en local o con Docker)
3. Abrir `http://localhost:8000` → debe devolver el JSON de bienvenida
4. Abrir `http://localhost:5173` → debe mostrar la pantalla de login
5. Iniciar sesión con las credenciales de prueba proporcionadas

Con esto queda comprobado que el backend responde, el frontend carga y la autenticación funciona.

### Verificación del pipeline de IA (opcional)

Para ejecutar manualmente un ciclo completo del scheduler (ingesta, IA, almacenamiento y notificaciones opcionales):

```bash
cd backend
source venv/bin/activate
python -m app.core.scheduler
```

Este comando ejecuta **una pasada completa** y termina. Requiere:

- Archivos `.env` configurados
- Ollama corriendo en el sistema con el modelo `llama3.1`

Las notificaciones de Teams son opcionales y se pueden omitir en la demostración.

## Tests

El proyecto incluye tests automatizados en el backend:

| Tipo         | Cantidad | Comando                              |
| ------------ | -------- | ------------------------------------ |
| Unitarios    | 33       | `pytest tests/unitarios`           |
| Integración | 23       | `pytest tests/integracion -rs -vv` |

Los tests se organizan en dos bloques claramente diferenciados:

- **Tests unitarios**: validan la lógica interna del sistema (API, deduplicación, pipeline, hashing, notificaciones y scheduler). No dependen del estado de periódicos externos y, por tanto, su comportamiento debe ser determinista.
- **Tests de integración**: validan el comportamiento real del sistema contra Supabase y contra fuentes externas de noticias mediante tres estrategias de extracción: **RSS** como vía principal, **scraping HTML** como respaldo y **browser automation con Playwright** como último fallback.

Para ejecutarlos:

```bash
cd backend
source venv/bin/activate
pytest tests/unitarios          # Tests unitarios
pytest tests/integracion -rs -vv  # Tests de integración reales (necesitan red)
```

Si se desea lanzar toda la batería del backend en una sola orden:

```bash
pytest
```

### Interpretación de los resultados

En los tests unitarios, el resultado esperado es que todos los casos pasen correctamente. En los tests de integración, pueden aparecer casos marcados como `SKIPPED` sin que esto implique un fallo del backend. Esto ocurre cuando una fuente externa:

- no devuelve artículos en ese momento,
- cambia su estructura HTML/XML,
- aplica bloqueos anti-bot,
- o está temporalmente caída o sin novedades.

En este proyecto, esos `SKIPPED` se consideran una **omisión controlada** ante dependencias de terceros, y no un error funcional de la aplicación.

La estrategia recomendada de explotación prioriza **RSS** por su mayor estabilidad, dejando **scraper** y **browser** como mecanismos de resiliencia para fuentes concretas.

## Resolución de problemas

| Problema                                        | Solución                                                                              |
| ----------------------------------------------- | -------------------------------------------------------------------------------------- |
| Los puertos `8000` o `5173` están ocupados | Cerrar la aplicación que los está usando antes de arrancar                           |
| `ollama: command not found`                   | Instalar Ollama desde https://ollama.com/                                              |
| El frontend no conecta con el backend           | Comprobar que `VITE_API_URL` en `frontend/.env` apunta a `http://localhost:8000` |
| Error de credenciales de Supabase               | Verificar que los valores en los `.env` coinciden con los proporcionados             |
