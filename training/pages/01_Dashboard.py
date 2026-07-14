import streamlit as st
import pandas as pd
from pathlib import Path
import re

from config import (
    DATA_DIR, IMAGES_DIR, TABULAR_DIR, MODELS_DIR,
    RESULTS_DIR, FALLBACK_MODELS_DIR, DRIVE_BASE,
)

MODEL_CATEGORIES = [
    ("CNN (EfficientNet)", ["cnn_efficientnet_", "best_cnn_efficientnet"], [".keras", ".h5"]),
    ("Ensemble (CNN+Clínico)", ["ensemble_"], [".keras"]),
    ("Hybrid CNN-RF Extractor", ["hybrid_cnn_rf_extractor_"], [".keras"]),
    ("Hybrid CNN-RF Classifier", ["hybrid_cnn_rf_classifier_"], [".pkl"]),
    ("Tabular (XGBoost)", ["tabular_"], [".pkl"]),
    ("Tabular (RF)", ["rf_tabular_"], [".pkl"]),
]


def classify_model(filename: str):
    for label, prefixes, extensions in MODEL_CATEGORIES:
        ext = Path(filename).suffix.lower()
        if ext not in extensions:
            continue
        for prefix in prefixes:
            if filename.startswith(prefix):
                return label
    return "Otro"


def get_model_type(filename: str) -> str:
    label = classify_model(filename)
    if "CNN" in label and "Extractor" in label:
        return "Hybrid"
    if "CNN" in label:
        return "CNN"
    if "Ensemble" in label:
        return "Ensemble"
    if "Hybrid" in label or "Classifier" in label:
        return "Hybrid"
    if "XGBoost" in label:
        return "Tabular"
    if "RF" in label or "Random" in label:
        return "Tabular"
    return "Unknown"

st.title("📊 Dashboard del Sistema")
st.markdown("Bienvenido al panel de control del sistema de detección de cáncer de mama.")

drive_available = Path(DRIVE_BASE).exists()
st.info(
    f"**Ruta base:** `{DRIVE_BASE}`  \n"
    f"{'✅ Google Drive detectado' if drive_available else '⚠️ Google Drive no montado'}"
    if not drive_available else
    f"**Ruta base:** `{DRIVE_BASE}`  \n✅ Google Drive montado correctamente"
)

col1, col2, col3, col4 = st.columns(4)

csv_files = list(DATA_DIR.glob("*.csv")) if DATA_DIR.exists() else []
total_csv = len(csv_files)
col1.metric("Archivos CSV", total_csv)

model_files = []
for md in [MODELS_DIR, FALLBACK_MODELS_DIR]:
    if md.exists():
        for f in md.glob("*"):
            if f.suffix in (".keras", ".h5", ".pkl"):
                model_files.append(f)

model_types = {}
for f in model_files:
    t = get_model_type(f.name)
    model_types.setdefault(t, set()).add(f.name)

unique_types = len(model_types)
total_models = len(model_files)
col2.metric("Modelos Totales", f"{total_models} ({unique_types} tipos)")

if TABULAR_DIR.exists():
    wis_path = TABULAR_DIR / "data.csv"
    if wis_path.exists():
        df = pd.read_csv(wis_path)
        total_cases = len(df)
        malignant = int((df["diagnosis"] == "M").sum()) if "diagnosis" in df.columns else 0
        benign = total_cases - malignant
        col3.metric("Casos Wisconsin", total_cases)
        col4.metric("Malignos / Benignos", f"{malignant} / {benign}")
    else:
        col3.metric("Casos Wisconsin", "N/A")
        col4.metric("Malignos / Benignos", "N/A")
else:
    col3.metric("Casos Wisconsin", "Sin datos")
    col4.metric("Malignos / Benignos", "Sin datos")

st.markdown("---")
st.subheader("📁 Archivos de Datos (CSV)")

tab1, tab2 = st.tabs(["📂 Google Drive", "📂 Local (backend/CSVFiles)"])

with tab1:
    if DATA_DIR.exists():
        data = []
        for f in csv_files:
            size_kb = f.stat().st_size / 1024
            data.append({"Archivo": f.name, "Tamaño (KB)": f"{size_kb:.1f}"})
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.warning(f"Ruta no encontrada: `{DATA_DIR}`")

with tab2:
    local_dir = FALLBACK_MODELS_DIR.parent / "CSVFiles"
    if local_dir.exists():
        data = []
        for f in local_dir.glob("*.csv"):
            size_kb = f.stat().st_size / 1024
            data.append({"Archivo": f.name, "Tamaño (KB)": f"{size_kb:.1f}"})
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.warning(f"Ruta no encontrada: `{local_dir}`")

st.subheader("📦 Modelos Entrenados")
for label, md in [("Google Drive", MODELS_DIR), ("Local backend/models", FALLBACK_MODELS_DIR)]:
    if md.exists():
        files = [f for f in md.glob("*") if f.suffix in (".keras", ".h5", ".pkl")]
        if not files:
            continue
        st.markdown(f"**{label}**")
        data = []
        for f in files:
            size_mb = f.stat().st_size / (1024 * 1024)
            data.append({
                "Tipo": classify_model(f.name),
                "Modelo": f.name,
                "Tamaño (MB)": f"{size_mb:.2f}",
            })
        df = pd.DataFrame(data)
        st.dataframe(df.sort_values("Tipo"), use_container_width=True)

with st.expander("📊 Resumen por Tipo de Modelo"):
    rows = []
    for cat_label, _, _ in MODEL_CATEGORIES:
        count = sum(1 for f in model_files if classify_model(f.name) == cat_label)
        if count > 0:
            rows.append({"Tipo": cat_label, "Cantidad": count})
    if rows:
        st.dataframe(pd.DataFrame(rows).set_index("Tipo"), use_container_width=True)

st.markdown("---")
st.subheader("🚀 Flujo de Trabajo Recomendado")
st.markdown(
    """
1. **📋 EDA** → Explora y visualiza los datasets
2. **🧠 Entrenamiento** → Entrena modelos clásicos (XGBoost, Random Forest)  
   *(Para CNN/Ensemble pesado, usa Google Colab con GPU)*
3. **🔁 Validación Cruzada** → Evalúa robustez con K-Fold
4. **⚙️ Hiperparámetros** → Encuentra la mejor configuración
5. **📈 Pruebas Estadísticas** → McNemar, Wilcoxon entre modelos
6. **📑 Reportes** → Genera PDF, Word, Excel con resultados
"""
)
