"""
Encapsula todo lo relacionado al modelo de deep learning:
- Carga única en memoria (singleton) al iniciar la app.
- Preprocesamiento de imagen idéntico al usado en el entrenamiento (Colab).
- Predicción con manejo de errores.
"""
import io
import logging
import time
from typing import Optional

import cv2
import numpy as np
from PIL import Image

from app.config import settings

logger = logging.getLogger("model_handler")


class ModelLoadError(Exception):
    """Se lanza cuando el modelo no pudo cargarse."""


class InvalidImageError(Exception):
    """Se lanza cuando la imagen subida no puede procesarse."""


class ModelHandler:
    """
    Carga el modelo una sola vez (patrón singleton a nivel de proceso) y
    expone un método predict() que recibe bytes de imagen cruda y devuelve
    la clase, la confianza y las probabilidades por clase.
    """

    def __init__(self):
        self._model = None
        self._model_loaded = False
        self._load_error: Optional[str] = None

    def load(self) -> None:
        """Carga el modelo a memoria. Se llama una vez al iniciar la app (startup event)."""
        # Import perezoso de tensorflow: acelera el arranque si algo falla antes,
        # y evita cargar TF completo si solo se está corriendo /health en un smoke test.
        import tensorflow as tf

        try:
            logger.info(f"Cargando modelo desde: {settings.MODEL_PATH}")
            self._model = tf.keras.models.load_model(settings.MODEL_PATH)
            self._model_loaded = True
            logger.info("Modelo cargado correctamente.")
        except Exception as exc:  # noqa: BLE001 - queremos capturar cualquier fallo de carga
            self._model_loaded = False
            self._load_error = str(exc)
            logger.error(f"Error cargando el modelo: {exc}")
            # No relanzamos aquí: dejamos que /health reporte "unhealthy" y que
            # /predict devuelva 503, en vez de tumbar el proceso completo.

    @property
    def is_loaded(self) -> bool:
        return self._model_loaded

    @property
    def load_error(self) -> Optional[str]:
        return self._load_error

    # ------------------------------------------------------------------ #
    # Preprocesamiento
    # ------------------------------------------------------------------ #
    @staticmethod
    def _apply_clahe_rgb(image: np.ndarray) -> np.ndarray:
        """Mismo CLAHE usado en el pipeline de entrenamiento (canal L de LAB)."""
        image = image.astype(np.uint8)
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        merged = cv2.merge((cl, a, b))
        return cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)

    def _preprocess(self, raw_bytes: bytes) -> np.ndarray:
        """
        Convierte los bytes subidos por el usuario en el tensor que espera el modelo:
        resize -> (opcional) CLAHE -> normalizado [0,1] -> batch de 1.
        """
        try:
            image = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        except Exception as exc:
            raise InvalidImageError(f"No se pudo decodificar la imagen: {exc}") from exc

        image = image.resize(settings.IMG_SIZE)
        array = np.array(image)

        if settings.APPLY_CLAHE:
            array = self._apply_clahe_rgb(array)

        array = array.astype(np.float32) / 255.0
        return np.expand_dims(array, axis=0)  # (1, H, W, 3)

    # ------------------------------------------------------------------ #
    # Predicción
    # ------------------------------------------------------------------ #
    def predict(self, raw_bytes: bytes) -> dict:
        if not self._model_loaded:
            raise ModelLoadError(self._load_error or "El modelo no está cargado.")

        start = time.perf_counter()
        tensor = self._preprocess(raw_bytes)
        raw_output = self._model.predict(tensor, verbose=0)

        # Soporta tanto salida sigmoid (1 neurona) como softmax (2 neuronas).
        raw_output = np.asarray(raw_output).reshape(-1)
        if raw_output.shape[0] == 1:
            malignant_prob = float(raw_output[0])
            benign_prob = 1.0 - malignant_prob
        else:
            benign_prob, malignant_prob = float(raw_output[0]), float(raw_output[1])

        label_idx = 1 if malignant_prob >= settings.PREDICTION_THRESHOLD else 0
        label = settings.CLASS_NAMES[label_idx]
        confidence = malignant_prob if label_idx == 1 else benign_prob

        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            "label": label,
            "confidence": confidence,
            "benign_prob": benign_prob,
            "malignant_prob": malignant_prob,
            "processing_time_ms": elapsed_ms,
        }


# Instancia única compartida por toda la app
model_handler = ModelHandler()