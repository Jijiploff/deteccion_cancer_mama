import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DRIVE_BASE = os.getenv("DRIVE_BASE", "/content/drive/MyDrive/DataSet")

_is_windows = sys.platform == "win32"

if _is_windows and not os.path.exists(DRIVE_BASE):
    _user_home = Path.home()
    _candidates = [
        Path("G:/Mi unidad/DataSet"),
        Path("F:/Mi unidad/DataSet"),
        Path("E:/Mi unidad/DataSet"),
        _user_home / "Google Drive" / "DataSet",
        _user_home / "Mi unidad" / "DataSet",
    ]
    for _p in _candidates:
        if _p.exists():
            DRIVE_BASE = str(_p)
            break

DATA_DIR = Path(os.getenv("TRAINING_DATA_DIR", str(Path(DRIVE_BASE) / "CSVFiles")))
IMAGES_DIR = Path(os.getenv("TRAINING_IMAGES_DIR", str(Path(DRIVE_BASE) / "BreastCancer_Images" / "jpeg")))
TABULAR_DIR = Path(os.getenv("TRAINING_TABULAR_DIR", str(Path(DRIVE_BASE) / "BreastCancer_Tabular")))
DATABASE_DIR = Path(os.getenv("TRAINING_DATABASE_DIR", str(Path(DRIVE_BASE) / "Database")))

MODELS_DIR = Path(os.getenv("TRAINING_MODELS_DIR", str(Path(DRIVE_BASE) / "Models")))
RESULTS_DIR = Path(os.getenv("TRAINING_RESULTS_DIR", str(Path(DRIVE_BASE) / "Resultados")))
FALLBACK_MODELS_DIR = BASE_DIR / "backend" / "models"

RANDOM_STATE = int(os.getenv("RANDOM_STATE", "42"))
TEST_SIZE = float(os.getenv("TEST_SIZE", "0.2"))
VAL_SIZE = float(os.getenv("VAL_SIZE", "0.2"))

IMG_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 5
LEARNING_RATE = 1e-4
PATIENCE = 10

DEFAULT_N_FOLDS = 5

APP_TITLE = "Sistema de Detección de Cáncer de Mama - Training Dashboard"
APP_ICON = "🩺"

RESULTS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
