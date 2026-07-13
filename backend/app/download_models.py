import logging
import os
from pathlib import Path

from app.config import settings

logger = logging.getLogger("download_models")


def _ensure_dir(path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def download_model(file_id: str, output_path: str, model_name: str, retries: int = 3) -> bool:
    if not file_id:
        logger.warning(
            "No se proporcionó FILE_ID para %s. "
            "Asignalo como variable de entorno en backend/.env",
            model_name,
        )
        return False

    if os.path.isfile(output_path):
        logger.info("%s ya existe en %s, saltando descarga", model_name, output_path)
        return True

    _ensure_dir(output_path)
    logger.info("Descargando %s desde Google Drive (file_id=%s)...", model_name, file_id)

    import gdown

    for attempt in range(1, retries + 1):
        try:
            gdown.download(id=file_id, output=output_path, quiet=False)
            if os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
                logger.info(
                    "%s descargado correctamente (%d bytes)",
                    model_name,
                    os.path.getsize(output_path),
                )
                return True
            logger.warning("Intento %d/%d: archivo vacío o no creado", attempt, retries)
        except Exception as exc:
            logger.error("Intento %d/%d falló para %s: %s", attempt, retries, model_name, exc)

    logger.error("No se pudo descargar %s después de %d intentos", model_name, retries)
    return False


def download_all_models():
    models = [
        (settings.CNN_MODEL_FILE_ID, settings.CNN_MODEL_PATH, "CNN (EfficientNet)"),
        (settings.ENSEMBLE_MODEL_FILE_ID, settings.ENSEMBLE_MODEL_PATH, "Ensemble (CNN+Clínico)"),
        (settings.TABULAR_MODEL_FILE_ID, settings.TABULAR_MODEL_PATH, "XGBoost (Wisconsin)"),
    ]

    results = []
    for file_id, output_path, name in models:
        ok = download_model(file_id, output_path, name)
        results.append((name, ok))

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    download_all_models()
