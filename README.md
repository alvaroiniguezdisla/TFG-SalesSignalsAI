# SalesSignalsAI

Plataforma web de monitorización de noticias empresariales para ventas B2B. El sistema recoge noticias de fuentes RSS, las analiza con un modelo de IA local (Ollama + LLaMA 3.1), las deduplica y las presenta en un dashboard personalizado para que los equipos comerciales identifiquen oportunidades de venta.

Desarrollado como Trabajo de Fin de Grado en CEU San Pablo en colaboración con HP.

---

## Repositorio Oficial (GitHub)

El código fuente de este proyecto para la evaluación académica se encuentra alojado en GitHub:
**🔗 URL del repositorio:** [https://github.com/alvaroiniguezdisla/TFG-SalesSignalsAI](https://github.com/alvaroiniguezdisla/TFG-SalesSignalsAI)

Para probar la aplicación en tu entorno local, el primer paso es clonar este repositorio en tu máquina:

```bash
git clone https://github.com/alvaroiniguezdisla/TFG-SalesSignalsAI.git
cd TFG-SalesSignalsAI
```

Una vez clonado, sigue los pasos de configuración detallados a continuación.

---

## Índice

1. [Arquitectura](#arquitectura)
2. [Requisitos previos](#requisitos-previos)
3. [Paso 1 — Configurar las variables de entorno](#paso-1--configurar-las-variables-de-entorno)
4. [Paso 2 — Despliegue 100% automatizado con Docker](#paso-2--despliegue-100-automatizado-con-docker)
5. [Paso 3 — Despliegue sin Docker (desarrollo local)](#paso-3--despliegue-sin-docker-desarrollo-local)
6. [Paso 4 — Acceder con usuario administrador](#paso-4--acceder-con-usuario-administrador)
7. [Paso 5 — Verificar las noticias y ejecutar el pipeline](#paso-5--verificar-las-noticias-y-ejecutar-el-pipeline)
8. [Notificaciones por Microsoft Teams (opcional)](#notificaciones-por-microsoft-teams-opcional)
9. [Comandos de prueba y operación](#comandos-de-prueba-y-operación)
10. [Guía de usuario](#guía-de-usuario)

---

## Arquitectura

| Capa | Tecnología |
|---|---|
| Backend (API) | Python 3.9 + FastAPI + Uvicorn |
| Frontend (web) | React 19 + Vite 7 + React Router 7 |
| Base de datos y autenticación | Supabase (PostgreSQL + Auth) |
| Motor de IA | Ollama con LLaMA 3.1 (inferencia local) |
| Servidor web frontend | Nginx (en Docker) |
| Contenedores | Docker + Docker Compose |
| Notificaciones (opcional) | Microsoft Graph API / Microsoft Teams |

El backend se comunica con Supabase para leer y escribir datos, y con Ollama para el análisis de noticias. El frontend se comunica tanto con el backend (para obtener noticias y ejecutar el pipeline) como directamente con Supabase (para autenticación y feedback de usuarios).

```
[Navegador]
    │
    ├──► [Frontend React — puerto 5173 / 80]
    │         │
    │         ├──► [Backend FastAPI — puerto 8000]
    │         │         │
    │         │         ├──► [Supabase — base de datos]
    │         │         └──► [Ollama — IA local — red interna Docker]
    │         │
    │         └──► [Supabase — autenticación y feedback]
```

---

## Requisitos previos

### Requisitos de hardware (Ollama)

El modelo de inteligencia artificial (LLaMA 3.1) se ejecuta localmente, ya sea dentro del contenedor de Docker o mediante una instalación manual de Ollama. Para que funcione correctamente y el tiempo de respuesta sea aceptable, se requiere:
- **Mínimo:** 8 GB de memoria RAM libre.
- **Recomendado:** 16 GB o más de memoria RAM.

> Si tu equipo tiene recursos muy limitados, la inferencia del modelo será extremadamente lenta o fallará al intentar cargar en memoria.

### Configuración recomendada de Docker Desktop

Si se ejecuta el proyecto con Docker, no basta con que el ordenador tenga memoria RAM suficiente: Docker Desktop debe tener memoria asignada en su propia configuración.

Antes de arrancar el proyecto, se recomienda revisar:

```text
Docker Desktop -> Settings -> Resources -> Advanced
```

Configuración recomendada:

| Recurso | Valor recomendado |
|---|---|
| Memory limit | 10-12 GB |
| Swap | 4 GB |
| CPU limit | 6-8 CPU |

Con menos memoria asignada, Ollama puede arrancar correctamente pero fallar durante la clasificación con un error similar a:

```text
model requires more system memory
```

### Qué hay que instalar en tu máquina

Para la ejecución recomendada con Docker, solo es necesario instalar Docker Desktop. Ollama y Python únicamente son necesarios si se decide ejecutar el backend manualmente sin Docker.

| Herramienta | Versión mínima | Para qué se usa |
|---|---|---|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | 24.x | Ejecutar los contenedores (incluye Docker Compose) |
| [Ollama](https://ollama.com) | Opcional | Solo necesario si se ejecuta el backend sin Docker |
| Python | 3.9 o 3.10 | Solo necesario si se ejecuta el backend sin Docker |

### Qué no hay que instalar

**Supabase** es un servicio en la nube. No se instala en tu máquina: el entorno de demostración utilizado para la evaluación se configura mediante los archivos `.env`.

**Ollama** tampoco debe instalarse manualmente si se usa el despliegue recomendado con Docker: `docker compose up --build` arranca el contenedor de Ollama y descarga el modelo `llama3.1` automáticamente.

---

## Paso 1 — Configurar las variables de entorno

El proyecto requiere un archivo `.env` para el backend y otro para el frontend. Para facilitar la evaluación del tribunal y al mismo tiempo mantener las buenas prácticas de seguridad en este repositorio público, **las claves del entorno de demostración se proporcionan exclusivamente en la Memoria del TFG (Sección 5.2 - Despliegue de la Aplicación)**.

### Backend

1. Copia el archivo de ejemplo:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Abre `backend/.env` e introduce las claves que encontrarás en la memoria académica.

### Frontend

1. Copia el archivo de ejemplo:
   ```bash
   cp frontend/.env.example frontend/.env
   ```
2. Abre `frontend/.env` e introduce las claves que encontrarás en la memoria académica.

---

## Paso 2 — Despliegue 100% automatizado con Docker

Esta es la forma recomendada para ejecutar el proyecto de manera reproducible, sin instalar dependencias locales.

### 2.1 Requisitos

- Docker Desktop en ejecución.
- Docker Desktop con memoria suficiente asignada (ver "Configuración recomendada de Docker Desktop").
- Los archivos `backend/.env` y `frontend/.env` completados (Paso 1).

### 2.2 Construir y arrancar los contenedores

Desde la raíz del repositorio (`TFG-SalesSignalsAI/`):

```bash
docker compose up --build
```

Este comando se encarga de todo el ciclo de vida:
1. Inicia el contenedor de la IA (Ollama) y descarga automáticamente el modelo `llama3.1` en segundo plano (este primer paso puede tardar unos minutos ya que el modelo pesa 4,7 GB).
2. Construye y arranca el backend (FastAPI).
3. Construye y arranca el frontend (Vite/Nginx).

### 2.3 Acceder a la aplicación

| Servicio | URL |
|---|---|
| Frontend (aplicación web) | http://localhost:5173 |
| Backend (API) | http://localhost:8000 |
| Documentación de la API | http://localhost:8000/docs |

### 2.4 Detener los contenedores

```bash
docker compose down
```

---

## Paso 3 — Despliegue sin Docker (desarrollo local)

Usa esta opción si prefieres ejecutar el código directamente en tu máquina, por ejemplo para depurar o desarrollar.

### Backend

En macOS:

```bash
cd backend
/usr/bin/python3 -m venv venv
source venv/bin/activate
python --version
python -m ensurepip --upgrade
python -m pip install "pip==24.3.1"
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

En Linux:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
python --version
python -m ensurepip --upgrade
python -m pip install "pip==24.3.1"
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

En Windows PowerShell:

```powershell
cd backend

# Comprueba las versiones disponibles y usa Python 3.9 o 3.10
py -0p
py -3.10 -m venv venv

.\venv\Scripts\Activate.ps1
python --version
python -m ensurepip --upgrade
python -m pip install "pip==24.3.1"
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

El backend queda disponible en `http://localhost:8000`.

> Para desarrollar y reiniciar automáticamente al cambiar código, puedes añadir `--reload` al comando de Uvicorn. Para una demo o ejecución estable, especialmente si el proyecto está dentro de iCloud Drive, es mejor arrancarlo sin `--reload`.

### Frontend

Abre una segunda terminal:

```bash
# 1. Entra en la carpeta del frontend
cd frontend

# 2. Instala las dependencias de Node
npm install

# 3. Arranca el servidor de desarrollo
npm run dev
```

El frontend queda disponible en `http://localhost:5173`.

---

## Paso 4 — Acceder con usuario administrador

Para la evaluación del TFG se usa el entorno de Supabase ya configurado y proporcionado junto con el proyecto. No es necesario crear una instancia nueva de Supabase ni ejecutar consultas SQL manuales.

El usuario administrador de evaluación ya está creado en ese entorno. Las credenciales de acceso se indican en la memoria académica.

1. Abre la aplicación en http://localhost:5173.
2. Inicia sesión con el usuario administrador de evaluación.
3. Accede al **Panel de administración** desde el dashboard principal.

### Crear usuarios adicionales

Una vez que ya tienes un usuario administrador, puedes crear usuarios adicionales directamente desde el panel de administración de la aplicación sin necesidad de tocar Supabase.

---

## Paso 5 — Verificar las noticias y ejecutar el pipeline

El entorno de demostración indicado en la memoria incluye noticias precargadas para que el dashboard tenga contenido desde el primer arranque.

1. Entra en la aplicación web con el usuario administrador de evaluación.
2. Abre el **Dashboard** principal y comprueba que aparecen las noticias demo.
3. Si quieres obtener noticias nuevas, entra con un usuario administrador y navega al panel de **Administración**.
4. Pulsa el botón para **Ejecutar Pipeline**. Esto hará que el backend descargue noticias de las fuentes RSS y las analice usando Ollama.
5. Una vez termine el proceso, vuelve al **Dashboard** principal para ver las noticias actualizadas.

Para comprobar el flujo completo del scheduler desde terminal (ingesta, IA, guardado en Supabase y notificaciones si Teams está configurado), ejecuta:

```bash
docker compose exec backend python -m app.core.scheduler
```

El botón de la aplicación sirve para lanzar el pipeline de extracción y análisis. El comando anterior fuerza una ejecución completa del scheduler sin esperar a la ejecución automática programada.

---

## Notificaciones por Microsoft Teams (opcional)

El sistema incluye soporte para enviar notificaciones automáticas por Microsoft Teams cuando el pipeline detecta noticias relevantes. Esta funcionalidad forma parte de la arquitectura del proyecto, pero **no se activa en el entorno de evaluación**, ya que requiere credenciales corporativas de Microsoft/Azure que no se distribuyen junto con el repositorio.

La aplicación puede ejecutarse, probarse y evaluarse correctamente sin configurar Teams. En ese caso, el pipeline seguirá realizando la ingesta, el análisis con IA y el guardado de noticias en Supabase.

### Requisitos

Para activar esta integración en un entorno corporativo real sería necesario disponer de una aplicación registrada en Azure/Microsoft y de las credenciales correspondientes.

### Configuración

Si se dispone de esas credenciales, la integración se configura mediante variables de entorno en `backend/.env`:

```env
GRAPH_TENANT_ID="tu-tenant-id"
GRAPH_CLIENT_ID="tu-client-id"
GRAPH_SCOPES="User.Read Chat.ReadWrite ChatMessage.Send"
TEAMS_TARGET_USER_EMAIL="correo-destino@empresa.com"
```

En el contexto de este TFG, esta parte queda documentada como integración opcional y no es necesaria para la demostración principal de la aplicación.

---

## Comandos de prueba y operación

Estos comandos sirven para comprobar que el sistema funciona y para lanzar procesos manuales.

### Si la aplicación está levantada con Docker

Ejecuta los comandos desde la raíz del repositorio (`TFG-SalesSignalsAI/`), con los contenedores activos.

```bash
docker compose up --build
```

| Quiero... | Comando |
|---|---|
| Ver logs del backend | `docker compose logs -f backend` |
| Ejecutar todos los tests | `docker compose exec backend pytest` |
| Ejecutar solo tests unitarios | `docker compose exec backend pytest tests/unitarios` |
| Ejecutar solo tests de integración | `docker compose exec backend pytest tests/integracion` |
| Ejecutar un test concreto | `docker compose exec backend pytest tests/unitarios/test_planificador.py -q` |
| Probar ingesta sin IA ni base de datos | `docker compose exec backend python -m scripts.manual_ingesta` |
| Ejecutar ingesta + IA + guardado en Supabase | `docker compose exec backend python -m scripts.manual_pipeline_completo` |
| Enviar notificaciones de Teams, solo si se han configurado credenciales | `docker compose exec backend python -m scripts.manual_notificador` |
| Ejecutar scheduler completo en una sola pasada | `docker compose exec backend python -m app.core.scheduler` |

### Si ejecutas el backend sin Docker

Ejecuta los comandos desde `TFG-SalesSignalsAI/backend/`, con el entorno virtual activado.

| Quiero... | Comando |
|---|---|
| Ejecutar todos los tests | `pytest` |
| Ejecutar solo tests unitarios | `pytest tests/unitarios` |
| Ejecutar solo tests de integración | `pytest tests/integracion` |
| Probar ingesta sin IA ni base de datos | `python -m scripts.manual_ingesta` |
| Ejecutar ingesta + IA + guardado en Supabase | `python -m scripts.manual_pipeline_completo` |
| Enviar notificaciones de Teams, solo si se han configurado credenciales | `python -m scripts.manual_notificador` |
| Ejecutar scheduler completo en una sola pasada | `python -m app.core.scheduler` |

El scheduler se inicia automáticamente al arrancar el backend y queda programado para ejecutarse cada 6 horas. El comando del scheduler sirve para forzar una ejecución manual sin esperar.

> Los tests de integración pueden requerir conexión a internet, credenciales válidas de Supabase y servicios externos disponibles. Para una comprobación rápida, ejecuta primero los tests unitarios.

---

## Guía de usuario

Una vez que la aplicación está en marcha, consulta el archivo [GUIA_USUARIO.md](GUIA_USUARIO.md) para aprender a:

- Navegar el dashboard de señales comerciales.
- Filtrar y priorizar noticias.
- Consultar el análisis de IA de cada noticia.
- Gestionar el perfil y las preferencias.
- Administrar usuarios, fuentes y configuración (rol administrador).
