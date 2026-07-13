import logging
import time
import uuid
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, status, Form, Depends
from fastapi.security import HTTPBearer

from app.auth import create_access_token, verify_password, get_current_user, require_user, USERS
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
    ModelResult,
    HistoryResponse,
    HistoryItem,
    HealthResponse,
)

setup_logging()
logger = logging.getLogger("main")

APP_START_TIME = time.time()
prediction_history: deque = deque(maxlen=settings.HISTORY_MAX_ITEMS)

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicación, cargando modelos...")
    model_handler.load()
    yield
    logger.info("Apagando aplicación.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.get("/health", response_model=HealthResponse, tags=["monitoreo"])
async def health_check():
    uptime = time.time() - APP_START_TIME
    loaded = model_handler.models_loaded
    overall = "healthy" if any(loaded.values()) else "unhealthy"
    return HealthResponse(
        status=overall,
        models_loaded=loaded,
        model_path=settings.CNN_MODEL_PATH,
        uptime_seconds=round(uptime, 2),
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )


def compute_consensus(model_results: list[dict]) -> tuple[str, str, float]:
    labels = [r["model_label"] for r in model_results if r["status"] == "success"]
    if not labels:
        return "disagreement", "BENIGN", 0.0
    benign_count = labels.count("BENIGN")
    malignant_count = labels.count("MALIGNANT")
    total = len(labels)
    if benign_count == total or malignant_count == total:
        consensus = "full_agreement"
    elif benign_count > malignant_count or malignant_count > benign_count:
        consensus = "majority"
    else:
        consensus = "disagreement"
    best = max(model_results, key=lambda r: r["confidence"] if r["status"] == "success" else 0)
    return consensus, best["model_label"], best["confidence"]


@app.post("/predict", response_model=PredictionResponse, tags=["diagnóstico"])
@limiter.limit(settings.RATE_LIMIT_PREDICT)
async def predict(
    request: Request,
    file: UploadFile = File(...),
    assessment: Optional[float] = Form(None),
    subtlety: Optional[float] = Form(None),
    age: Optional[float] = Form(None),
    density: Optional[float] = Form(None),
    radius_mean: Optional[float] = Form(None),
    texture_mean: Optional[float] = Form(None),
    perimeter_mean: Optional[float] = Form(None),
    area_mean: Optional[float] = Form(None),
    smoothness_mean: Optional[float] = Form(None),
    compactness_mean: Optional[float] = Form(None),
    concavity_mean: Optional[float] = Form(None),
    concave_points_mean: Optional[float] = Form(None),
    symmetry_mean: Optional[float] = Form(None),
    fractal_dimension_mean: Optional[float] = Form(None),
    radius_se: Optional[float] = Form(None),
    texture_se: Optional[float] = Form(None),
    perimeter_se: Optional[float] = Form(None),
    area_se: Optional[float] = Form(None),
    smoothness_se: Optional[float] = Form(None),
    compactness_se: Optional[float] = Form(None),
    concavity_se: Optional[float] = Form(None),
    concave_points_se: Optional[float] = Form(None),
    symmetry_se: Optional[float] = Form(None),
    fractal_dimension_se: Optional[float] = Form(None),
    radius_worst: Optional[float] = Form(None),
    texture_worst: Optional[float] = Form(None),
    perimeter_worst: Optional[float] = Form(None),
    area_worst: Optional[float] = Form(None),
    smoothness_worst: Optional[float] = Form(None),
    compactness_worst: Optional[float] = Form(None),
    concavity_worst: Optional[float] = Form(None),
    concave_points_worst: Optional[float] = Form(None),
    symmetry_worst: Optional[float] = Form(None),
    fractal_dimension_worst: Optional[float] = Form(None),
):
    if not model_handler.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ningún modelo está disponible.",
        )

    raw_bytes = await validate_upload_image(file)

    clinical_data = None
    if assessment is not None:
        clinical_data = [
            assessment or 3.0,
            subtlety or 3.0,
            age or 50.0,
            density or 2.0,
        ]

    wisconsin_data = None
    wisconsin_fields = [
        radius_mean, texture_mean, perimeter_mean, area_mean,
        smoothness_mean, compactness_mean, concavity_mean, concave_points_mean,
        symmetry_mean, fractal_dimension_mean,
        radius_se, texture_se, perimeter_se, area_se,
        smoothness_se, compactness_se, concavity_se, concave_points_se,
        symmetry_se, fractal_dimension_se,
        radius_worst, texture_worst, perimeter_worst, area_worst,
        smoothness_worst, compactness_worst, concavity_worst, concave_points_worst,
        symmetry_worst, fractal_dimension_worst,
    ]
    if any(v is not None for v in wisconsin_fields):
        defaults = settings.WISCONSIN_DEFAULTS
        feature_names = settings.WISCONSIN_FEATURES
        wisconsin_data = [
            v if v is not None else defaults[name]
            for v, name in zip(wisconsin_fields, feature_names)
        ]

    try:
        results = model_handler.predict_all(raw_bytes, clinical_data, wisconsin_data)
    except InvalidImageError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Error inesperado durante la predicción")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno procesando la imagen.",
        ) from exc

    if not results:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo ejecutar ningún modelo.",
        )

    consensus, best_label, best_confidence = compute_consensus(results)
    best_result = max(results, key=lambda r: r["confidence"] if r["status"] == "success" else 0)

    prediction_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc)

    response = PredictionResponse(
        prediction_id=prediction_id,
        filename=file.filename or "imagen_sin_nombre",
        timestamp=timestamp,
        consensus=consensus,
        models=[ModelResult(**r) for r in results],
        label=best_label,
        confidence=best_confidence,
        probabilities=PredictionProbabilities(
            benign=round(best_result["benign_prob"], 4),
            malignant=round(best_result["malignant_prob"], 4),
        ),
        processing_time_ms=round(best_result["processing_time_ms"], 2),
        warning="Confianza baja: se recomienda revisión adicional" if best_confidence < 0.65 else None,
    )

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
        f"consenso={consensus} | label={response.label} | confianza={response.confidence:.3f}"
    )

    return response


@app.get("/history", response_model=HistoryResponse, tags=["diagnóstico"])
async def get_history():
    return HistoryResponse(total=len(prediction_history), items=list(prediction_history))


@app.delete("/history", tags=["diagnóstico"])
async def clear_history():
    prediction_history.clear()
    return {"message": "Historial limpiado."}


@app.post("/auth/login", tags=["autenticación"])
async def login(username: str = Form(...), password: str = Form(...)):
    expected = USERS.get(username)
    if not expected or not verify_password(password, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    token = create_access_token(username)
    return {"access_token": token, "token_type": "bearer", "username": username}


@app.get("/auth/me", tags=["autenticación"])
async def auth_me(username: str = Depends(require_user)):
    return {"username": username}


@app.get("/", tags=["monitoreo"])
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
