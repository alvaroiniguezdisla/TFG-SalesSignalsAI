# 📡 SalesSignalsAI (Observatorio de Señales)

Este proyecto es una herramienta de inteligencia de ventas que monitoriza fuentes de información pública (como El País) para detectar "señales" de negocio relevantes para cuentas clave.

## 🚀 Cómo Arrancar el Proyecto

Necesitas dos terminales abiertas (una para el cerebro y otra para la cara).

### 1. Backend (Cerebro Python)
```bash
cd backend
source venv/bin/activate  # En Windows: venv\Scripts\activate
uvicorn main:app --reload
```
El backend estará escuchando en: `http://localhost:8000`

### 2. Frontend (Interfaz React)
```bash
cd frontend
npm install  # Solo la primera vez
npm run dev
```
La web se abrirá en: `http://localhost:5173`

## 🏗️ Estructura del Proyecto

*   **`backend/`**: API REST en FastAPI.
    *   `main.py`: Controlador de rutas.
    *   `scraper.py`: Lógica de extracción de datos (BeautifulSoup).
*   **`frontend/`**: SPA en React + Vite.
    *   `src/services/`: Comunicación con el backend.
    *   `src/pages/`: Vistas principales (Dashboard).
    *   `src/components/`: Piezas reutilizables (Tarjetas de noticias).

## 🛠️ Tecnologías
*   **Backend**: Python 3.12, FastAPI, BeautifulSoup4.
*   **Frontend**: React 18, Vite.
