#model_handler.py
import io
import logging
import time
import gc
import os
import threading
from typing import Optional

import cv2
import numpy as np
from PIL import Image

from app.config import settings

logger = logging.getLogger("model_handler")


class InvalidImageError(Exception):
    pass


class ModelHandler:
    def __init__(self):
        self._load_errors: dict[str, Optional[str]] = {}
        self._model_status: dict[str, str] = {}
        self._tabular_rf_model = None
        self._hybrid_classifier_model = None
        self._inference_lock = threading.Lock()

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

    def load(self):
        checks = [
            ("CNN", settings.CNN_MODEL_PATH),
            ("TabularRF", settings.TABULAR_MODEL_PATH),
            ("HybridExtractor", settings.EXTRACTOR_HYBRID_MODEL_PATH),
            ("HybridClassifier", settings.CLASIFIER_HYBRID_MODEL_PATH),
        ]
        for name, path in checks:
            if os.path.isfile(path):
                self._model_status[name] = "available"
                self._load_errors[name] = None
                logger.info(f"{name}: archivo encontrado en {path}")
            else:
                self._model_status[name] = "error"
                self._load_errors[name] = f"Archivo no encontrado: {path}"
                logger.error(f"{name}: archivo no encontrado en {path}")

        # Los .pkl son livianos (RandomForest de sklearn), se cachean permanentemente
        if self._model_status.get("TabularRF") == "available":
            try:
                import joblib
                self._tabular_rf_model = joblib.load(settings.TABULAR_MODEL_PATH)
                logger.info("Tabular RF cargado y cacheado en memoria")
            except Exception as exc:
                self._model_status["TabularRF"] = "error"
                self._load_errors["TabularRF"] = str(exc)
                logger.error(f"Error cargando Tabular RF: {exc}")

        if self._model_status.get("HybridClassifier") == "available":
            try:
                import joblib
                self._hybrid_classifier_model = joblib.load(settings.CLASIFIER_HYBRID_MODEL_PATH)
                logger.info("Hybrid classifier (RF) cargado y cacheado en memoria")
            except Exception as exc:
                self._model_status["HybridClassifier"] = "error"
                self._load_errors["HybridClassifier"] = str(exc)
                logger.error(f"Error cargando Hybrid classifier: {exc}")

    @property
    def is_loaded(self) -> bool:
        return any(s == "available" for s in self._model_status.values())

    @property
    def models_loaded(self) -> dict[str, bool]:
        return {k: v == "available" for k, v in self._model_status.items()}

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
    def _preprocess_hybrid_extractor(raw_bytes: bytes) -> np.ndarray:
        file_bytes = np.frombuffer(raw_bytes, np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if image is None:
            raise InvalidImageError("No se pudo decodificar la imagen para el extractor híbrido")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, settings.IMG_SIZE)
        image = image.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image = (image - mean) / std
        return np.expand_dims(image, axis=0)

    def _run_cnn(self, raw_bytes: bytes) -> Optional[dict]:
        if self._model_status.get("CNN") != "available":
            return None
        with self._inference_lock:
            start = time.perf_counter()
            self._patch_quantization_config()
            import keras

            model = None
            try:
                logger.info(f"Cargando CNN bajo demanda desde: {settings.CNN_MODEL_PATH}")
                model = keras.models.load_model(settings.CNN_MODEL_PATH)
                tensor = self._preprocess_cnn(raw_bytes)
                raw_output = model.predict(tensor, verbose=0)
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
            except Exception as exc:
                logger.error(f"Error en inferencia CNN: {exc}")
                return self._model_unavailable_result("CNN (EfficientNet)", str(exc), status="error")
            finally:
                del model
                keras.backend.clear_session()
                gc.collect()

    def _run_tabular_rf(self, wisconsin_data: list[float]) -> Optional[dict]:
        if self._tabular_rf_model is None:
            return None
        start = time.perf_counter()
        features = np.array(wisconsin_data, dtype=np.float32).reshape(1, -1)
        proba = self._tabular_rf_model.predict_proba(features)[0]
        malignant_prob = float(proba[1])
        benign_prob = float(proba[0])
        label_idx = 1 if malignant_prob >= settings.PREDICTION_THRESHOLD else 0
        label = settings.CLASS_NAMES[label_idx]
        confidence = malignant_prob if label_idx == 1 else benign_prob
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "model_name": "Tabular RF (Wisconsin)",
            "model_label": label,
            "confidence": round(confidence, 4),
            "benign_prob": round(benign_prob, 4),
            "malignant_prob": round(malignant_prob, 4),
            "processing_time_ms": round(elapsed_ms, 2),
            "status": "success",
            "error": None,
        }

    def _run_hybrid(self, raw_bytes: bytes) -> Optional[dict]:
        if self._model_status.get("HybridExtractor") != "available" or self._hybrid_classifier_model is None:
            return None
        with self._inference_lock:
            start = time.perf_counter()
            self._patch_quantization_config()
            import keras

            model = None
            try:
                logger.info(f"Cargando extractor híbrido bajo demanda desde: {settings.EXTRACTOR_HYBRID_MODEL_PATH}")
                model = keras.models.load_model(settings.EXTRACTOR_HYBRID_MODEL_PATH)
                tensor = self._preprocess_hybrid_extractor(raw_bytes)
                feature_vector = model.predict(tensor, verbose=0)
                feature_vector = np.asarray(feature_vector).reshape(1, -1)

                proba = self._hybrid_classifier_model.predict_proba(feature_vector)[0]
                malignant_prob = float(proba[1])
                benign_prob = float(proba[0])
                label_idx = 1 if malignant_prob >= settings.PREDICTION_THRESHOLD else 0
                label = settings.CLASS_NAMES[label_idx]
                confidence = malignant_prob if label_idx == 1 else benign_prob
                elapsed_ms = (time.perf_counter() - start) * 1000
                return {
                    "model_name": "Híbrido (CNN extractor + RF)",
                    "model_label": label,
                    "confidence": round(confidence, 4),
                    "benign_prob": round(benign_prob, 4),
                    "malignant_prob": round(malignant_prob, 4),
                    "processing_time_ms": round(elapsed_ms, 2),
                    "status": "success",
                    "error": None,
                }
            except Exception as exc:
                logger.error(f"Error en inferencia híbrida: {exc}")
                return self._model_unavailable_result("Híbrido (CNN extractor + RF)", str(exc), status="error")
            finally:
                del model
                keras.backend.clear_session()
                gc.collect()

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

    def predict_all(self, raw_bytes: bytes, wisconsin_data: Optional[list[float]] = None) -> list[dict]:
        results = []

        if self._model_status.get("CNN") == "available":
            cnn_result = self._run_cnn(raw_bytes)
            if cnn_result:
                results.append(cnn_result)
        else:
            results.append(self._model_unavailable_result(
                "CNN (EfficientNet)", self._load_errors.get("CNN") or "Modelo no disponible.", status="error"))

        if self._tabular_rf_model is None:
            results.append(self._model_unavailable_result(
                "Tabular RF (Wisconsin)", self._load_errors.get("TabularRF") or "Modelo no disponible.", status="error"))
        elif wisconsin_data is not None and len(wisconsin_data) == 30:
            rf_result = self._run_tabular_rf(wisconsin_data)
            if rf_result:
                results.append(rf_result)
        else:
            results.append(self._model_unavailable_result(
                "Tabular RF (Wisconsin)", "Faltan variables Wisconsin para este modelo."))

        if self._model_status.get("HybridExtractor") != "available" or self._hybrid_classifier_model is None:
            reason = self._load_errors.get("HybridExtractor") or self._load_errors.get("HybridClassifier") or "Modelo no disponible."
            results.append(self._model_unavailable_result("Híbrido (CNN extractor + RF)", reason, status="error"))
        else:
            hybrid_result = self._run_hybrid(raw_bytes)
            if hybrid_result:
                results.append(hybrid_result)

        return results


model_handler = ModelHandler()