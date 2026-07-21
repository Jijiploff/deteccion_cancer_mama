import logging
import os
from pathlib import Path

logger = logging.getLogger("download_models")

HF_REPO_ID = os.getenv("HF_REPO_ID", "usuario/tu-repo-aqui")
HF_TOKEN = os.getenv("HF_TOKEN", None)

MODEL_FILES = [
    "cnn_efficientnet_20260707_061411.keras",
    "ensemble_20260707_061411.keras",
    "hybrid_cnn_rf_extractor_20260713_130540.keras",
    "hybrid_cnn_rf_classifier_20260713_130540.pkl",
    "tabular_20260707_061411.pkl",
    "rf_tabular_20260713_130540.pkl",
    "best_cnn_efficientnet.h5",
]


def download_models(models_dir: Path, repo_id: str = HF_REPO_ID, token: str = HF_TOKEN):
    """
    Descarga los modelos desde HuggingFace Hub si no existen localmente.
    """
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        logger.error("huggingface-hub no está instalado. pip install huggingface-hub")
        return False

    models_dir = Path(models_dir)
    models_dir.mkdir(exist_ok=True, parents=True)

    all_ok = True
    for filename in MODEL_FILES:
        dest = models_dir / filename
        if dest.exists():
            size_mb = dest.stat().st_size / (1024 * 1024)
            logger.info(f"Ya existe: {filename} ({size_mb:.2f} MB)")
            continue

        try:
            logger.info(f"Descargando {filename} desde {repo_id}...")
            downloaded = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                token=token,
                local_dir=models_dir,
                local_dir_use_symlinks=False,
            )
            size_mb = Path(downloaded).stat().st_size / (1024 * 1024)
            logger.info(f"  OK {filename} ({size_mb:.2f} MB)")
        except Exception as e:
            logger.warning(f"  Error descargando {filename}: {e}")
            all_ok = False

    return all_ok
