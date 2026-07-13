"""
Configuración central del sistema.
Todos los valores sensibles o dependientes del entorno se leen de variables
de entorno, con valores por defecto razonables para desarrollo local.
"""
import os
from pathlib import Path


class Settings:
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    CNN_MODEL_PATH: str = os.getenv("CNN_MODEL_PATH", str(BASE_DIR / "models" / "cnn_efficientnet_20260707_061411.keras"))
    ENSEMBLE_MODEL_PATH: str = os.getenv("ENSEMBLE_MODEL_PATH", str(BASE_DIR / "models" / "ensemble_20260707_061411.keras"))
    TABULAR_MODEL_PATH: str = os.getenv("TABULAR_MODEL_PATH", str(BASE_DIR / "models" / "tabular_20260707_061411.pkl"))
    WISCONSIN_CSV_PATH: str = os.getenv("WISCONSIN_CSV_PATH", str(BASE_DIR / "CSVFiles" / "data.csv"))

    CNN_MODEL_FILE_ID: str = os.getenv("CNN_MODEL_FILE_ID", "")
    ENSEMBLE_MODEL_FILE_ID: str = os.getenv("ENSEMBLE_MODEL_FILE_ID", "")
    TABULAR_MODEL_FILE_ID: str = os.getenv("TABULAR_MODEL_FILE_ID", "")

    IMG_SIZE: tuple = (224, 224)
    APPLY_CLAHE: bool = os.getenv("APPLY_CLAHE", "true").lower() == "true"
    CLASS_NAMES: list = ["BENIGN", "MALIGNANT"]
    PREDICTION_THRESHOLD: float = float(os.getenv("PREDICTION_THRESHOLD", "0.5"))

    WISCONSIN_FEATURES: list = [
        "radius_mean", "texture_mean", "perimeter_mean", "area_mean",
        "smoothness_mean", "compactness_mean", "concavity_mean", "concave points_mean",
        "symmetry_mean", "fractal_dimension_mean",
        "radius_se", "texture_se", "perimeter_se", "area_se",
        "smoothness_se", "compactness_se", "concavity_se", "concave points_se",
        "symmetry_se", "fractal_dimension_se",
        "radius_worst", "texture_worst", "perimeter_worst", "area_worst",
        "smoothness_worst", "compactness_worst", "concavity_worst", "concave points_worst",
        "symmetry_worst", "fractal_dimension_worst",
    ]
    WISCONSIN_DEFAULTS: dict = {
        "radius_mean": 14.127, "texture_mean": 19.290, "perimeter_mean": 91.969, "area_mean": 654.889,
        "smoothness_mean": 0.096, "compactness_mean": 0.104, "concavity_mean": 0.089, "concave points_mean": 0.049,
        "symmetry_mean": 0.181, "fractal_dimension_mean": 0.063,
        "radius_se": 0.405, "texture_se": 1.217, "perimeter_se": 2.866, "area_se": 40.337,
        "smoothness_se": 0.007, "compactness_se": 0.025, "concavity_se": 0.032, "concave points_se": 0.012,
        "symmetry_se": 0.021, "fractal_dimension_se": 0.004,
        "radius_worst": 16.269, "texture_worst": 25.677, "perimeter_worst": 107.261, "area_worst": 880.583,
        "smoothness_worst": 0.132, "compactness_worst": 0.254, "concavity_worst": 0.272, "concave points_worst": 0.115,
        "symmetry_worst": 0.290, "fractal_dimension_worst": 0.084,
    }
    CLINICAL_FEATURES: list = ["assessment", "subtlety", "age", "density"]

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

    # --- Autenticación JWT ---
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

    # --- App ---
    APP_NAME: str = "Breast Cancer Detection API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development | production
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()