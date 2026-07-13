# Imagen base ligera con Python 3.10
FROM python:3.10-slim

# Dependencias del sistema que necesita opencv-python-headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias primero (aprovecha cache de Docker si no cambian)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la app, modelos y datos de referencia
COPY app/ ./app/
COPY models/ ./models/
COPY CSVFiles/ ./CSVFiles/

# Descargar modelos desde Google Drive si se proporcionaron FILE_ID como build args
# Usa: docker build --build-arg CNN_MODEL_FILE_ID=... ...
ARG CNN_MODEL_FILE_ID
ARG ENSEMBLE_MODEL_FILE_ID
ARG TABULAR_MODEL_FILE_ID
ENV CNN_MODEL_FILE_ID=$CNN_MODEL_FILE_ID \
    ENSEMBLE_MODEL_FILE_ID=$ENSEMBLE_MODEL_FILE_ID \
    TABULAR_MODEL_FILE_ID=$TABULAR_MODEL_FILE_ID
RUN python -m app.download_models || echo "Descarga opcional omitida (sin FILE_IDs)"

# Render inyecta la variable de entorno PORT; exponemos 8000 como referencia local
EXPOSE 8000

# Usamos sh -c para poder usar la variable $PORT que Render define en runtime
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]