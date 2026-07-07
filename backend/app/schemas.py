"""
Esquemas Pydantic: definen la forma de las respuestas de la API.
Esto le da al frontend (y a Swagger /docs) un contrato claro y tipado.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PredictionProbabilities(BaseModel):
    benign: float = Field(..., ge=0, le=1, description="Probabilidad de que sea benigno (0-1)")
    malignant: float = Field(..., ge=0, le=1, description="Probabilidad de que sea maligno (0-1)")


class PredictionResponse(BaseModel):
    prediction_id: str
    label: str = Field(..., description="'BENIGN' o 'MALIGNANT'")
    confidence: float = Field(..., ge=0, le=1, description="Confianza de la predicción ganadora (0-1)")
    probabilities: PredictionProbabilities
    processing_time_ms: float
    timestamp: datetime
    filename: str
    warning: Optional[str] = Field(
        default=None,
        description="Aviso opcional, p. ej. si la confianza es baja",
    )


class HistoryItem(BaseModel):
    prediction_id: str
    filename: str
    label: str
    confidence: float
    timestamp: datetime


class HistoryResponse(BaseModel):
    total: int
    items: list[HistoryItem]


class HealthResponse(BaseModel):
    status: str  # "healthy" | "degraded" | "unhealthy"
    model_loaded: bool
    model_path: str
    uptime_seconds: float
    version: str
    environment: str


class ErrorResponse(BaseModel):
    error: str
    detail: str