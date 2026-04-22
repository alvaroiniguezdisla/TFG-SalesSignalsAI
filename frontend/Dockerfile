FROM node:20-alpine AS build

WORKDIR /app

# Copiar dependencias e instalar
COPY package*.json ./
RUN npm install

# Copiar código fuente (incluye .env para que Vite inyecte las variables)
COPY . .

# Compilar la app React a archivos estáticos
RUN npm run build

# --- Fase 2: Servir con Nginx ---
FROM nginx:alpine

# Copiar los archivos compilados desde la fase anterior
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
