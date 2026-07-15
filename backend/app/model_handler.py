import io
import logging
import time
from typing import Optional

import cv2
import numpy as np
from PIL import Image

from app.config import settings
from app.download_models import download_model

logger = logging.getLogger("model_handler")


class ModelLoadError(Exception):
    pass


class InvalidImageError(Exception):
    pass


class ModelHandler:
    def __init__(self):
        self._models: dict[str, object] = {}
        self._load_errors: dict[str, Optional[str]] = {}
        self._model_status: dict[str, str] = {}

    @staticmethod
    def _patch_quantization_config():
        try:
            from keras.src.layers.core.dense import Dense
            original_init = Dense.__init__
            def patched_init(self, *args, **kwargs):
                kwargs.pop("quantization_config", None)
                original_init(self, *args, **kwargs)
            Dense.__init__ = patched_init
        except ImportError:
            pass

    def _load_cnn(self) -> Optional[object]:
        self._patch_quantization_config()
        import keras
        logger.info(f"Cargando CNN desde: {settings.CNN_MODEL_PATH}")
        return keras.models.load_model(settings.CNN_MODEL_PATH)

    def _load_ensemble(self) -> Optional[object]:
        self._patch_quantization_config()
        import keras
        logger.info(f"Cargando Ensemble desde: {settings.ENSEMBLE_MODEL_PATH}")
        return keras.models.load_model(settings.ENSEMBLE_MODEL_PATH)

    def _load_tabular(self) -> Optional[object]:
        import joblib
        logger.info(f"Cargando XGBoost desde: {settings.TABULAR_MODEL_PATH}")
        return joblib.load(settings.TABULAR_MODEL_PATH)

    def load(self):
        models_config = [
            ("CNN", self._load_cnn, settings.CNN_MODEL_FILE_ID, settings.CNN_MODEL_PATH),
            ("Ensemble", self._load_ensemble, settings.ENSEMBLE_MODEL_FILE_ID, settings.ENSEMBLE_MODEL_PATH),
            ("XGBoost", self._load_tabular, settings.TABULAR_MODEL_FILE_ID, settings.TABULAR_MODEL_PATH),
        ]
        for name, loader, file_id, output_path in models_config:
            try:
                if file_id:
                    download_model(file_id, output_path, name)
                else:
                    logger.info(f"Sin FILE_ID para {name}, usando archivo local: {output_path}")
                self._models[name] = loader()
                self._model_status[name] = "loaded"
                self._load_errors[name] = None
                logger.info(f"Modelo {name} cargado correctamente.")
            except Exception as exc:
                self._models[name] = None
                self._model_status[name] = "error"
                self._load_errors[name] = str(exc)
                logger.error(f"Error cargando {name}: {exc}")

    @property
    def is_loaded(self) -> bool:
        return any(s == "loaded" for s in self._model_status.values())

    @property
    def models_loaded(self) -> dict[str, bool]:
        return {k: v == "loaded" for k, v in self._model_status.items()}

    @staticmethod
    def _apply_clahe_rgb(image: np.ndarray) -> np.ndarray:
        image = image.astype(np.uint8)
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        merged = cv2.merge((cl, a, b))
        return cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)

    def _preprocess_cnn(self, raw_bytes: bytes) -> np.ndarray:
        try:
            image = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        except Exception as exc:
            raise InvalidImageError(f"No se pudo decodificar la imagen: {exc}") from exc
        image = image.resize(settings.IMG_SIZE)
        array = np.array(image)
        if settings.APPLY_CLAHE:
            array = self._apply_clahe_rgb(array)
        array = array.astype(np.float32) / 255.0
        return np.expand_dims(array, axis=0)

    @staticmethod
    def _preprocess_ensemble(raw_bytes: bytes) -> np.ndarray:
        file_bytes = np.frombuffer(raw_bytes, np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if image is None:
            raise InvalidImageError("No se pudo decodificar la imagen para Ensemble")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, settings.IMG_SIZE)
        image = image.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image = (image - mean) / std
        return np.expand_dims(image, axis=0)

    def _run_cnn(self, raw_bytes: bytes) -> Optional[dict]:
        if self._models.get("CNN") is None:
            return None
        start = time.perf_counter()
        tensor = self._preprocess_cnn(raw_bytes)
        raw_output = self._models["CNN"].predict(tensor, verbose=0)
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
            "model_name": "CNN (EfficientNet)",
            "model_label": label,
            "confidence": round(confidence, 4),
            "benign_prob": round(benign_prob, 4),
            "malignant_prob": round(malignant_prob, 4),
            "processing_time_ms": round(elapsed_ms, 2),
            "status": "success",
            "error": None,
        }

    def _run_ensemble(self, raw_bytes: bytes, clinical_data: list[float]) -> Optional[dict]:
        if self._models.get("Ensemble") is None:
            return None
        start = time.perf_counter()
        image_tensor = self._preprocess_ensemble(raw_bytes)
        clinical_array = np.array(clinical_data, dtype=np.float32).reshape(1, -1)
        raw_output = self._models["Ensemble"].predict([image_tensor, clinical_array], verbose=0)
        malignant_prob = float(np.asarray(raw_output).reshape(-1)[0])
        benign_prob = 1.0 - malignant_prob
        label_idx = 1 if malignant_prob >= settings.PREDICTION_THRESHOLD else 0
        label = settings.CLASS_NAMES[label_idx]
        confidence = malignant_prob if label_idx == 1 else benign_prob
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "model_name": "Ensemble (CNN + Clínico)",
            "model_label": label,
            "confidence": round(confidence, 4),
            "benign_prob": round(benign_prob, 4),
            "malignant_prob": round(malignant_prob, 4),
            "processing_time_ms": round(elapsed_ms, 2),
            "status": "success",
            "error": None,
        }

    def _run_xgboost(self, wisconsin_data: list[float]) -> Optional[dict]:
        if self._models.get("XGBoost") is None:
            return None
        start = time.perf_counter()
        xgb = self._models["XGBoost"]
        features = np.array(wisconsin_data, dtype=np.float32).reshape(1, -1)
        proba = xgb.predict_proba(features)[0]
        malignant_prob = float(proba[1])
        benign_prob = float(proba[0])
        label_idx = 1 if malignant_prob >= settings.PREDICTION_THRESHOLD else 0
        label = settings.CLASS_NAMES[label_idx]
        confidence = malignant_prob if label_idx == 1 else benign_prob
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "model_name": "XGBoost (Wisconsin)",
            "model_label": label,
            "confidence": round(confidence, 4),
            "benign_prob": round(benign_prob, 4),
            "malignant_prob": round(malignant_prob, 4),
            "processing_time_ms": round(elapsed_ms, 2),
            "status": "success",
            "error": None,
        }

    def _model_unavailable_result(self, model_name: str, reason: str, status: str = "unavailable") -> dict:
        return {
            "model_name": model_name,
            "model_label": None,
            "confidence": None,
            "benign_prob": None,
            "malignant_prob": None,
            "processing_time_ms": None,
            "status": status,
            "error": reason,
        }

    def predict_all(self, raw_bytes: bytes,
                    clinical_data: Optional[list[float]] = None,
                    wisconsin_data: Optional[list[float]] = None) -> list[dict]:
        results = []
        if self._models.get("CNN") is not None:
            cnn_result = self._run_cnn(raw_bytes)
            if cnn_result:
                results.append(cnn_result)
        else:
            results.append(
                self._model_unavailable_result(
                    "CNN (EfficientNet)",
                    self._load_errors.get("CNN") or "Modelo no cargado.",
                    status="error" if self._load_errors.get("CNN") else "unavailable",
                )
            )

        if self._models.get("Ensemble") is None:
            results.append(
                self._model_unavailable_result(
                    "Ensemble (CNN + Clínico)",
                    self._load_errors.get("Ensemble") or "Modelo no cargado.",
                    status="error" if self._load_errors.get("Ensemble") else "unavailable",
                )
            )
        elif clinical_data is not None and len(clinical_data) == 4:
            ens_result = self._run_ensemble(raw_bytes, clinical_data)
            if ens_result:
                results.append(ens_result)
        else:
            results.append(
                self._model_unavailable_result(
                    "Ensemble (CNN + Clínico)",
                    "Faltan datos clínicos para este modelo.",
                )
            )

        if self._models.get("XGBoost") is None:
            results.append(
                self._model_unavailable_result(
                    "XGBoost (Wisconsin)",
                    self._load_errors.get("XGBoost") or "Modelo no cargado.",
                    status="error" if self._load_errors.get("XGBoost") else "unavailable",
                )
            )
        elif wisconsin_data is not None and len(wisconsin_data) == 30:
            xgb_result = self._run_xgboost(wisconsin_data)
            if xgb_result:
                results.append(xgb_result)
        else:
            results.append(
                self._model_unavailable_result(
                    "XGBoost (Wisconsin)",
                    "Faltan variables Wisconsin para este modelo.",
                )
            )

        return results


model_handler = ModelHandler()
