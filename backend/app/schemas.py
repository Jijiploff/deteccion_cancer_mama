from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ModelResult(BaseModel):
    model_name: str
    model_label: str = Field(..., description="BENIGN o MALIGNANT")
    confidence: float = Field(..., ge=0, le=1)
    benign_prob: float = Field(..., ge=0, le=1)
    malignant_prob: float = Field(..., ge=0, le=1)
    processing_time_ms: float
    status: str = Field(..., description="success | error | unavailable")
    error: Optional[str] = None


class PredictionProbabilities(BaseModel):
    benign: float = Field(..., ge=0, le=1)
    malignant: float = Field(..., ge=0, le=1)


class PredictionResponse(BaseModel):
    prediction_id: str
    filename: str
    timestamp: datetime
    consensus: str = Field(..., description="full_agreement | majority | disagreement")
    models: list[ModelResult]
    label: str = Field(..., description="Predicción del modelo más confiable")
    confidence: float = Field(..., ge=0, le=1)
    probabilities: PredictionProbabilities
    processing_time_ms: float
    warning: Optional[str] = None


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
    status: str
    models_loaded: dict[str, bool]
    model_path: Optional[str] = None
    uptime_seconds: float
    version: str
    environment: str


class ErrorResponse(BaseModel):
    error: str
    detail: str
