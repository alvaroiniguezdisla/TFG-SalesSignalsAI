FROM node:20-alpine AS build

WORKDIR /app

# Copiar dependencias e instalar
COPY package*.json ./
RUN npm install

# Copiar código fuente (incluye .env para que Vite inyecte las variables)
COPY . .

# Compilar la app React a archivos estáticos
RUN npm run build

# --- Fase 2: Servir con un servidor ligero ---
FROM node:20-alpine

WORKDIR /app

# Instalar un servidor estático mínimo
RUN npm install -g serve

# Copiar los archivos compilados desde la fase anterior
COPY --from=build /app/dist ./dist

EXPOSE 5173

# Servir la carpeta dist en el puerto 5173
CMD ["serve", "-s", "dist", "-l", "5173"]
