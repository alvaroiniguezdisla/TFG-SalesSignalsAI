# SalesSignalsAI

Plataforma web de monitorización de noticias empresariales para ventas B2B. El sistema recoge noticias de fuentes RSS, las analiza con un modelo de IA local (Ollama + LLaMA 3.1), las deduplica y las presenta en un dashboard personalizado para que los equipos comerciales identifiquen oportunidades de venta.

Desarrollado como Trabajo de Fin de Grado en CEU San Pablo en colaboración con HP.

---

## Índice

1. [Arquitectura](#arquitectura)
2. [Requisitos previos](#requisitos-previos)
3. [Paso 1 — Configurar Supabase](#paso-1--configurar-supabase)
4. [Paso 2 — Configurar las variables de entorno](#paso-2--configurar-las-variables-de-entorno)
5. [Paso 3 — Configurar Ollama](#paso-3--configurar-ollama)
6. [Paso 4 — Despliegue con Docker (recomendado)](#paso-4--despliegue-con-docker-recomendado)
7. [Paso 5 — Despliegue sin Docker (desarrollo local)](#paso-5--despliegue-sin-docker-desarrollo-local)
8. [Paso 6 — Crear el primer usuario administrador](#paso-6--crear-el-primer-usuario-administrador)
9. [Notificaciones por Microsoft Teams (opcional)](#notificaciones-por-microsoft-teams-opcional)
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
    │         │         └──► [Ollama — IA local — puerto 11434]
    │         │
    │         └──► [Supabase — autenticación y feedback]
```

---

## Requisitos previos

### Requisitos de hardware (Ollama)

El modelo de inteligencia artificial (LLaMA 3.1) se ejecuta de manera local en tu máquina. Para que funcione correctamente y el tiempo de respuesta sea aceptable, se requiere:
- **Mínimo:** 8 GB de memoria RAM libre.
- **Recomendado:** 16 GB o más de memoria RAM.

> Si tu equipo tiene recursos muy limitados, la inferencia del modelo será extremadamente lenta o fallará al intentar cargar en memoria.

### Qué hay que instalar en tu máquina

| Herramienta | Versión mínima | Para qué se usa |
|---|---|---|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | 24.x | Ejecutar los contenedores (incluye Docker Compose) |
| [Ollama](https://ollama.com) | cualquiera | Motor de IA local |

### Qué no hay que instalar

**Supabase** es un servicio en la nube. No se instala en tu máquina: simplemente creas una cuenta gratuita en [https://supabase.com](https://supabase.com) y usas su panel web para configurar la base de datos. El Paso 1 explica exactamente qué hacer.

---

## Paso 1 — Configurar Supabase

Supabase es el servicio de base de datos y autenticación del proyecto. Tiene un plan gratuito que es suficiente para este despliegue.

### 1.1 Crear el proyecto

1. Ve a [https://supabase.com](https://supabase.com) e inicia sesión o crea una cuenta.
2. Pulsa **New project**.
3. Elige un nombre para el proyecto (por ejemplo, `salessignalsai`).
4. Establece una contraseña para la base de datos. **Guárdala**, la necesitarás si alguna vez accedes directamente a Postgres.
5. Selecciona la región más cercana (por ejemplo, `West EU`).
6. Pulsa **Create new project** y espera a que termine el aprovisionamiento (aproximadamente 1 minuto).

### 1.2 Crear las tablas (esquema SQL)

El proyecto incluye un archivo SQL listo para ejecutar que crea todas las tablas, el trigger de registro y las políticas de seguridad.

1. En el menú lateral de tu proyecto de Supabase, ve a **SQL Editor**.
2. Pulsa **New query**.
3. Abre el archivo `supabase/schema.sql` de este repositorio y copia todo su contenido.
4. Pégalo en el editor de Supabase.
5. Pulsa **Run** (o `Ctrl + Enter`).
6. Verifica que no hay errores en el panel inferior.
7. Ve a **Table Editor** en el menú lateral y comprueba que aparecen estas 4 tablas:
   - `app_config`
   - `noticias`
   - `profiles`
   - `news_feedback`

> Si ves el mensaje `already exists` en alguna tabla, es normal si estás re-ejecutando el script. El script usa `CREATE TABLE IF NOT EXISTS` para evitar errores.

### 1.3 Obtener las tres claves de API

El proyecto necesita tres valores de Supabase: la URL del proyecto y dos claves. A continuación se explica dónde encontrar cada una.

#### URL del proyecto (`SUPABASE_URL` y `VITE_SUPABASE_URL`)

Ruta en el panel de Supabase:
```
Tu proyecto → Integrations → Data API → API URL
```
Copia la URL y elimina `/rest/v1/` del final. El resultado debe tener esta forma:
```
https://<tu-proyecto>.supabase.co
```

#### Clave pública (`SUPABASE_KEY` y `VITE_SUPABASE_ANON_KEY`)

Es la clave de uso general, segura para el frontend. Ruta en el panel de Supabase:
```
Tu proyecto → Project Settings → API Keys → Publishable key
```
La clave empieza por `sb_publishable_...`.
Si tu panel muestra **Legacy API keys**, usa la clave `anon` de ahí. Es equivalente.

#### Clave privada de administrador (`SUPABASE_SERVICE_ROLE_KEY`)

Esta clave solo se usa en el backend para gestionar usuarios. Ruta en el panel de Supabase:
```
Tu proyecto → Project Settings → API Keys → Secret keys
```
La clave empieza por `sb_secret_...`.
Si tu panel muestra **Legacy API keys**, usa la clave `service_role` de ahí.

> **Importante:** La clave privada tiene permisos totales sobre la base de datos. Úsala únicamente en el backend y nunca la pongas en el frontend ni en un repositorio público.

---

## Paso 2 — Configurar las variables de entorno

El proyecto tiene dos archivos de variables de entorno: uno para el backend y otro para el frontend.

### Backend

1. Copia el archivo de ejemplo:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Abre `backend/.env` y rellena los valores con las claves obtenidas en el paso anterior:
   ```env
   # URL del proyecto Supabase
   SUPABASE_URL="https://TU-PROYECTO.supabase.co"

   # Clave pública (sb_publishable_... o anon)
   SUPABASE_KEY="TU_CLAVE_PUBLICA"

   # Clave privada de administrador (sb_secret_... o service_role)
   SUPABASE_SERVICE_ROLE_KEY="TU_CLAVE_PRIVADA"

   # Opcional: solo si se van a usar notificaciones de Teams
   GRAPH_TENANT_ID=""
   GRAPH_CLIENT_ID=""
   GRAPH_SCOPES="User.Read Chat.ReadWrite ChatMessage.Send"
   TEAMS_TARGET_USER_EMAIL=""
   ```

### Frontend

1. Copia el archivo de ejemplo:
   ```bash
   cp frontend/.env.example frontend/.env
   ```
2. Abre `frontend/.env` y rellénalo:
   ```env
   # URL del backend (no cambiar si usas Docker en local)
   VITE_API_URL="http://localhost:8000"

   # Los mismos valores de Supabase que en el backend
   VITE_SUPABASE_URL="https://TU-PROYECTO.supabase.co"
   VITE_SUPABASE_ANON_KEY="TU_CLAVE_PUBLICA"
   ```

> `VITE_SUPABASE_ANON_KEY` es la misma clave pública que pusiste en `SUPABASE_KEY` del backend.
> Si desplegas en un servidor con dominio propio, cambia `VITE_API_URL` por la URL pública del backend.

---

## Paso 3 — Configurar Ollama

Ollama es el motor de IA que el backend usa para analizar las noticias. Se ejecuta en tu máquina de forma local, fuera de Docker.

### 3.1 Instalar Ollama

Descarga e instala Ollama desde [https://ollama.com](https://ollama.com). Sigue el instalador para tu sistema operativo (Windows, macOS o Linux).

### 3.2 Descargar el modelo

Abre una terminal y ejecuta:

```bash
ollama pull llama3.1
```

La descarga puede tardar varios minutos dependiendo de tu conexión (el modelo pesa aproximadamente 4,7 GB).

### 3.3 Verificar que Ollama está activo

```bash
ollama list
```

Deberías ver `llama3.1` en la lista. Ollama queda activo en segundo plano automáticamente tras la instalación.

> El backend llama a Ollama en `http://localhost:11434`. Si usas Docker, el contenedor del backend accede a Ollama del anfitrión a través de `host.docker.internal:11434`, lo cual ya está configurado en el `docker-compose.yml`.

---

## Paso 4 — Despliegue con Docker (recomendado)

Esta es la forma más sencilla y reproducible de ejecutar el proyecto.

### 4.1 Requisitos

- Docker Desktop en ejecución.
- Los archivos `backend/.env` y `frontend/.env` completados (Paso 2).
- Ollama activo con el modelo descargado (Paso 3).

### 4.2 Construir y arrancar los contenedores

Desde la raíz del repositorio (`ceu-salessignalsai/`):

```bash
docker compose up --build
```

Este comando:
1. Construye la imagen del backend (Python + Playwright + dependencias).
2. Construye la imagen del frontend (Vite build + Nginx).
3. Arranca ambos contenedores.

La primera vez puede tardar entre 5 y 10 minutos por la descarga e instalación de dependencias.

### 4.3 Acceder a la aplicación

| Servicio | URL |
|---|---|
| Frontend (aplicación web) | http://localhost:5173 |
| Backend (API) | http://localhost:8000 |
| Documentación de la API | http://localhost:8000/docs |

### 4.4 Detener los contenedores

```bash
docker compose down
```

---

## Paso 5 — Despliegue sin Docker (desarrollo local)

Usa esta opción si prefieres ejecutar el código directamente en tu máquina, por ejemplo para depurar o desarrollar.

### Backend

```bash
# 1. Entra en la carpeta del backend
cd backend

# 2. Crea un entorno virtual de Python
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Instala los navegadores que usa Playwright
playwright install chromium

# 5. Arranca el servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

El backend queda disponible en `http://localhost:8000`.

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

## Paso 6 — Crear el primer usuario administrador

Al arrancar la aplicación por primera vez no hay ningún usuario creado. Para poder acceder al panel de administración necesitas al menos un usuario con rol `admin`.

### Opción A — Registro desde la aplicación y promoción manual

1. Abre la aplicación en http://localhost:5173.
2. Pulsa **Regístrate aquí** y crea una cuenta con tu correo y contraseña.
3. Vuelve a Supabase → **SQL Editor** y ejecuta la siguiente consulta, sustituyendo el correo:
   ```sql
   UPDATE public.profiles
   SET role = 'admin'
   WHERE email = 'tu-correo@ejemplo.com';
   ```
4. Recarga la aplicación e inicia sesión. Ahora tendrás acceso al **Panel de administración**.

### Opción B — Crear el usuario directamente desde el panel de administración

Una vez que ya tienes un usuario administrador, puedes crear usuarios adicionales directamente desde el panel de administración de la aplicación sin necesidad de tocar Supabase.

---

## Paso 7 — Obtener las primeras noticias

Al ejecutar el script de la base de datos (Paso 1), se han cargado automáticamente unas fuentes RSS y un prompt de IA por defecto. Sin embargo, el sistema arranca sin noticias hasta que el pipeline se ejecute por primera vez:

1. Entra en la aplicación web con tu usuario administrador recién creado.
2. Navega al panel de **Administración**.
3. Pulsa el botón para **Ejecutar Pipeline** (o equivalente). Esto hará que el backend empiece a descargar las noticias de las fuentes RSS y a analizarlas usando Ollama.
4. Una vez termine el proceso, vuelve al **Dashboard** principal para empezar a ver la inteligencia comercial generada.

---

## Notificaciones por Microsoft Teams (opcional)

El sistema puede enviar notificaciones automáticas por Teams cuando el pipeline detecta noticias relevantes. Esta integración es opcional y requiere una cuenta de Microsoft con acceso a Teams.

### Requisitos

- Una aplicación registrada en el portal de Azure con los permisos `User.Read`, `Chat.ReadWrite` y `ChatMessage.Send`.
- El `Tenant ID` y el `Client ID` de esa aplicación.

### Configuración

Rellena las siguientes variables en `backend/.env`:

```env
GRAPH_TENANT_ID="tu-tenant-id"
GRAPH_CLIENT_ID="tu-client-id"
GRAPH_SCOPES="User.Read Chat.ReadWrite ChatMessage.Send"
TEAMS_TARGET_USER_EMAIL="correo-destino@empresa.com"
```

La primera vez que el sistema intente enviar una notificación, el backend mostrará en consola un enlace de autenticación de Microsoft. Ábrelo en el navegador, inicia sesión con tu cuenta de Microsoft y autoriza los permisos. El token se guarda localmente y no hace falta repetir el proceso.

> En el contexto de este TFG, las notificaciones se envían únicamente al correo configurado en `TEAMS_TARGET_USER_EMAIL`.

---

## Guía de usuario

Una vez que la aplicación está en marcha, consulta el archivo [GUIA_USUARIO.md](GUIA_USUARIO.md) para aprender a:

- Navegar el dashboard de señales comerciales.
- Filtrar y priorizar noticias.
- Consultar el análisis de IA de cada noticia.
- Gestionar el perfil y las preferencias.
- Administrar usuarios, fuentes y configuración (rol administrador).
