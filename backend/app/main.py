"""
API RESTful para detección de cáncer de mama a partir de mamografías.

Endpoints:
    GET  /health           -> health check para monitoreo (Render lo usa para saber si el servicio está vivo)
    POST /predict          -> recibe una imagen y devuelve BENIGN/MALIGNANT + confianza
    GET  /history          -> últimas predicciones realizadas (almacenamiento en memoria)
    DELETE /history        -> limpia el historial

Ejecutar localmente:
    uvicorn app.main:app --reload --port 8000
"""
import logging
import time
import uuid
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.logging_config import setup_logging
from app.model_handler import model_handler, ModelLoadError, InvalidImageError
from app.security import validate_upload_image
from app.schemas import (
    PredictionResponse,
    PredictionProbabilities,
    HistoryResponse,
    HistoryItem,
    HealthResponse,
)

setup_logging()
logger = logging.getLogger("main")

# --- Estado en memoria (simple, no persistente entre reinicios) ---
APP_START_TIME = time.time()
prediction_history: deque = deque(maxlen=settings.HISTORY_MAX_ITEMS)

# --- Rate limiter ---
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: cargar el modelo UNA sola vez y mantenerlo en memoria (cache).
    logger.info("Iniciando aplicación, cargando modelo...")
    model_handler.load()
    yield
    # Shutdown: nada que liberar explícitamente, pero queda el hook por si acaso.
    logger.info("Apagando aplicación.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


# --- Headers de seguridad básicos ---
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# ---------------------------------------------------------------------- #
# Endpoints
# ---------------------------------------------------------------------- #
@app.get("/health", response_model=HealthResponse, tags=["monitoreo"])
async def health_check():
    """
    Health check para monitoreo (Render, uptime robots, etc.).
    Devuelve 200 siempre que el proceso esté vivo; el campo `status` indica
    si el modelo está realmente disponible para predecir.
    """
    uptime = time.time() - APP_START_TIME
    if model_handler.is_loaded:
        status_str = "healthy"
    else:
        status_str = "unhealthy"

    return HealthResponse(
        status=status_str,
        model_loaded=model_handler.is_loaded,
        model_path=settings.MODEL_PATH,
        uptime_seconds=round(uptime, 2),
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["diagnóstico"])
@limiter.limit(settings.RATE_LIMIT_PREDICT)
async def predict(request: Request, file: UploadFile = File(...)):
    """
    Recibe una mamografía (JPG/PNG, máx. 5MB) y devuelve la predicción del modelo.
    """
    if not model_handler.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El modelo no está disponible actualmente. Intenta más tarde.",
        )

    raw_bytes = await validate_upload_image(file)

    try:
        result = model_handler.predict(raw_bytes)
    except InvalidImageError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ModelLoadError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Error inesperado durante la predicción")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno procesando la imagen.",
        ) from exc

    prediction_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc)

    response = PredictionResponse(
        prediction_id=prediction_id,
        label=result["label"],
        confidence=result["confidence"],
        probabilities=PredictionProbabilities(
            benign=result["benign_prob"],
            malignant=result["malignant_prob"],
        ),
        processing_time_ms=round(result["processing_time_ms"], 2),
        timestamp=timestamp,
        filename=file.filename or "imagen_sin_nombre",
        warning="Confianza baja: se recomienda revisión adicional" if result["confidence"] < 0.65 else None,
    )

    # Guardar en historial (en memoria)
    prediction_history.appendleft(
        HistoryItem(
            prediction_id=prediction_id,
            filename=response.filename,
            label=response.label,
            confidence=response.confidence,
            timestamp=timestamp,
        )
    )

    logger.info(
        f"Predicción {prediction_id} | archivo={response.filename} | "
        f"label={response.label} | confianza={response.confidence:.3f}"
    )

    return response


@app.get("/history", response_model=HistoryResponse, tags=["diagnóstico"])
async def get_history():
    """
    Devuelve las últimas predicciones realizadas.
    NOTA: almacenamiento en memoria del proceso -> se pierde al reiniciar el
    servicio (por ejemplo, en cada deploy de Render). Para historial
    persistente entre despliegues, reemplazar por una base de datos
    (Postgres, SQLite con volumen persistente, etc.).
    """
    return HistoryResponse(total=len(prediction_history), items=list(prediction_history))


@app.delete("/history", tags=["diagnóstico"])
async def clear_history():
    prediction_history.clear()
    return {"message": "Historial limpiado."}


@app.get("/", tags=["monitoreo"])
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }