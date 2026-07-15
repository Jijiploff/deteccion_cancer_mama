import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DRIVE_BASE, DATA_DIR, IMAGES_DIR, TABULAR_DIR
from config import DATABASE_DIR, MODELS_DIR, RESULTS_DIR
from modules.eda import BreastCancerEDA

DRIVE_PATH = Path(DRIVE_BASE)
DRIVE_EXISTS = DRIVE_PATH.exists()

EXPECTED_DIRECTORIES = {
    "CSVFiles": DATA_DIR,
    "BreastCancer_Images/jpeg": IMAGES_DIR,
    "BreastCancer_Tabular": TABULAR_DIR,
    "Database": DATABASE_DIR,
    "Models": MODELS_DIR,
    "Resultados": RESULTS_DIR,
}

EXPECTED_CSV_FILES = [
    "calc_case_description_train_set.csv",
    "calc_case_description_test_set.csv",
    "mass_case_description_train_set.csv",
    "mass_case_description_test_set.csv",
    "meta.csv",
    "dicom_info.csv",
]


@pytest.fixture(scope="module")
def eda():
    if not DRIVE_EXISTS:
        pytest.skip("Google Drive no está montado")
    return BreastCancerEDA(str(DRIVE_PATH))


# ── Test 1: DRIVE_BASE resuelto ──────────────────────────────────────────────

def test_drive_base_resolved(request):
    assert DRIVE_BASE, "DRIVE_BASE está vacío"
    assert DRIVE_EXISTS, (
        f"La ruta {DRIVE_BASE} NO existe. "
        "Monta Google Drive Desktop o configura DRIVE_BASE en training/.env"
    )
    request.config._drive_summary["drive_base"] = str(DRIVE_BASE)
    request.config._drive_summary["drive_exists"] = True


# ── Test 2: Estructura de directorios ────────────────────────────────────────

def test_dataset_directory_structure(request):
    if not DRIVE_EXISTS:
        pytest.skip("Google Drive no está montado")
    faltantes = []
    presentes = []
    for nombre, path in EXPECTED_DIRECTORIES.items():
        if Path(path).exists():
            presentes.append(nombre)
        else:
            faltantes.append(nombre)
    request.config._drive_summary["directorios"] = presentes
    assert not faltantes, (
        f"Faltan directorios en Dataset: {faltantes}. "
        "Asegúrate de que Google Drive esté sincronizado"
    )


# ── Test 3: Archivos CSV ─────────────────────────────────────────────────────

def test_csv_files_present(request):
    if not DRIVE_EXISTS:
        pytest.skip("Google Drive no está montado")
    csv_info = []
    total_rows = 0
    for fname in EXPECTED_CSV_FILES:
        fpath = DATA_DIR / fname
        assert fpath.exists(), f"Falta archivo CSV: {fpath}"
        df = pd.read_csv(fpath)
        filas = len(df)
        total_rows += filas
        csv_info.append({
            "nombre": fname,
            "filas": filas,
            "bytes": fpath.stat().st_size,
        })
    request.config._drive_summary["csv_files"] = csv_info
    request.config._drive_summary["csv_total_filas"] = total_rows
    assert total_rows > 0, "Los CSV están vacíos"


# ── Test 4: Carpetas de imágenes legibles ────────────────────────────────────

def test_image_folders_readable(request):
    if not DRIVE_EXISTS:
        pytest.skip("Google Drive no está montado")
    assert IMAGES_DIR.exists(), f"Directorio de imágenes no existe: {IMAGES_DIR}"
    subdirs = [d for d in IMAGES_DIR.iterdir() if d.is_dir()]
    n_folders = len(subdirs)
    assert n_folders > 0, f"No hay subdirectorios en {IMAGES_DIR}"
    request.config._drive_summary["image_folders"] = n_folders
    folder_sample = list(subdirs)[:3]
    total_imgs = 0
    for folder in folder_sample:
        images = list(folder.iterdir())
        total_imgs += len(images)
        assert len(images) > 0, f"La carpeta {folder.name} no contiene imágenes"
    request.config._drive_summary["image_files"] = total_imgs


# ── Test 5: Datos tabulares (Wisconsin) ──────────────────────────────────────

def test_tabular_data_readable(request):
    if not DRIVE_EXISTS:
        pytest.skip("Google Drive no está montado")
    csv_path = TABULAR_DIR / "data.csv"
    assert csv_path.exists(), f"Falta data.csv en {TABULAR_DIR}"
    df = pd.read_csv(csv_path)
    assert len(df) > 0, "data.csv está vacío"
    assert "diagnosis" in df.columns, "data.csv no tiene columna 'diagnosis'"
    request.config._drive_summary["tabular_exists"] = True
    request.config._drive_summary["tabular_rows"] = len(df)
    request.config._drive_summary["tabular_cols"] = len(df.columns)


# ── Test 6: Instanciación de EDA ─────────────────────────────────────────────

def test_eda_instantiation(eda):
    assert isinstance(eda, BreastCancerEDA)
    assert eda.base_path == DRIVE_PATH
    assert eda.csv_path == DATA_DIR
    assert eda.images_path == IMAGES_DIR
    assert eda.tabular_path == TABULAR_DIR


# ── Test 7: EDA load_all_data ────────────────────────────────────────────────

def test_eda_load_all_data(eda):
    eda.load_all_data()
    assert eda.is_loaded, "EDA no cargó los datos correctamente"
    summary = eda.get_data_summary()
    assert summary["calcificaciones"] > 0, "No se cargaron calcificaciones"
    assert summary["masas"] > 0, "No se cargaron masas"
    assert summary["metadatos"] > 0, "No se cargaron metadatos"
    assert summary["wisconsin"] > 0, "No se cargaron datos Wisconsin"


# ── Test 8: Image mapping stats ──────────────────────────────────────────────

def test_eda_image_mapping(eda, request):
    if not eda.is_loaded:
        eda.load_all_data()
    stats = eda.get_image_mapping_stats()
    assert stats["series_en_meta"] > 0, "No hay SeriesInstanceUID en meta.csv"
    assert stats["carpetas_imagenes"] > 0, "No hay carpetas de imágenes"
    request.config._drive_summary["series_in_meta"] = stats["series_en_meta"]
    request.config._drive_summary["matching_series"] = stats["coincidencias"]


# ── Test 9: Conteo total de archivos ─────────────────────────────────────────

def test_total_file_count(request):
    if not DRIVE_EXISTS:
        pytest.skip("Google Drive no está montado")
    summary = request.config._drive_summary
    csv_count = len(summary.get("csv_files", []))
    img_count = summary.get("image_files", 0)
    tabular = 1 if summary.get("tabular_exists") else 0
    total = csv_count + img_count + tabular
    summary["total_archivos"] = max(total, csv_count + 1)
    assert total > 0, "No se encontraron archivos en el Dataset"


# ── Test 10: Variable de entorno tiene prioridad ─────────────────────────────

def test_env_override(monkeypatch, tmp_path):
    test_dataset = tmp_path / "DataSet"
    test_dataset.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("DRIVE_BASE", str(test_dataset))
    import importlib
    import config as cfg
    importlib.reload(cfg)
    assert cfg.DRIVE_BASE == str(test_dataset), (
        "DRIVE_BASE debería respetar la variable de entorno"
    )
