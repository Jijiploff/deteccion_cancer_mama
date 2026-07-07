# --- Etapa 1: build de la app React con Vite ---
FROM node:20-slim AS build

WORKDIR /app

# Copiar solo package.json si no existe package-lock.json
COPY package.json ./
RUN npm install  # Cambiar npm ci por npm install

COPY . .

# VITE_API_URL se "hornea" dentro del JS en build time
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# --- Etapa 2: servir el build estático con nginx ---
FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]