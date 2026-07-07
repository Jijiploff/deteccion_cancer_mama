# Imagen base ligera con Python 3.10
FROM python:3.10-slim

# Dependencias del sistema que necesita opencv-python-headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias primero (aprovecha cache de Docker si no cambian)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la app y el modelo entrenado
COPY app/ ./app/
COPY models/ ./models/

# Render inyecta la variable de entorno PORT; exponemos 8000 como referencia local
EXPOSE 8000

# Usamos sh -c para poder usar la variable $PORT que Render define en runtime
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]