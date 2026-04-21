# Imagen base oficial de Playwright — incluye Python 3.9 y Chromium preinstalado.
# Evita tener que instalar el navegador manualmente y garantiza compatibilidad.
FROM mcr.microsoft.com/playwright/python:v1.56.0-jammy

WORKDIR /app

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

EXPOSE 8000

# Arrancar Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
