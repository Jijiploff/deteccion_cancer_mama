"""
Configuración central del sistema.
Todos los valores sensibles o dependientes del entorno se leen de variables
de entorno, con valores por defecto razonables para desarrollo local.
"""
import os
from pathlib import Path


class Settings:
    # --- Rutas ---
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    MODEL_PATH: str = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "modelo_cancer_mama.keras"))

    # --- Modelo / preprocesamiento ---
    IMG_SIZE: tuple = (224, 224)
    APPLY_CLAHE: bool = os.getenv("APPLY_CLAHE", "true").lower() == "true"
    CLASS_NAMES: list = ["BENIGN", "MALIGNANT"]  # índice 0 y 1 del sigmoid/softmax
    PREDICTION_THRESHOLD: float = float(os.getenv("PREDICTION_THRESHOLD", "0.5"))

    # --- Validación de archivos ---
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_CONTENT_TYPES: set = {"image/jpeg", "image/jpg", "image/png"}
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png"}

    # --- CORS ---
    # En Render, define FRONTEND_URL como variable de entorno con tu dominio de Vercel.
    # Se admite una lista separada por comas para soportar preview deployments.
    FRONTEND_URLS: list = [
        url.strip()
        for url in os.getenv("FRONTEND_URL", "http://localhost:3000,http://localhost:5173").split(",")
        if url.strip()
    ]

    # --- Rate limiting ---
    RATE_LIMIT_PREDICT: str = os.getenv("RATE_LIMIT_PREDICT", "10/minute")
    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "60/minute")

    # --- Historial en memoria ---
    HISTORY_MAX_ITEMS: int = int(os.getenv("HISTORY_MAX_ITEMS", "50"))

    # --- App ---
    APP_NAME: str = "Breast Cancer Detection API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development | production
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()