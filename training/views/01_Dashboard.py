import streamlit as st
import pandas as pd
from pathlib import Path
import re

from config import (
    DATA_DIR, IMAGES_DIR, TABULAR_DIR, MODELS_DIR,
    RESULTS_DIR, FALLBACK_MODELS_DIR, DRIVE_BASE,
)
from modules.i18n import get_translation

lang = st.session_state.get("language", "es")

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
    return "Otro" if lang == "es" else "Other"


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

st.title(get_translation(lang, "dashboard.title"))
st.markdown(get_translation(lang, "dashboard.welcome"))

drive_available = Path(DRIVE_BASE).exists()
st.info(
    f"**{get_translation(lang, 'dashboard.base_path')}:** `{DRIVE_BASE}`  \n"
    f"{'✅ ' + get_translation(lang, 'dashboard.drive_detected') if drive_available else '⚠️ ' + get_translation(lang, 'dashboard.drive_not_mounted')}"
    if not drive_available else
    f"**{get_translation(lang, 'dashboard.base_path')}:** `{DRIVE_BASE}`  \n✅ {get_translation(lang, 'dashboard.drive_mounted_correctly')}"
)

col1, col2, col3, col4 = st.columns(4)

csv_files = list(DATA_DIR.glob("*.csv")) if DATA_DIR.exists() else []
total_csv = len(csv_files)
col1.metric(get_translation(lang, "dashboard.csv_files"), total_csv)

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
col2.metric(get_translation(lang, "dashboard.total_models"), f"{total_models} ({unique_types} {get_translation(lang, 'dashboard.total_models_sub')})")

if TABULAR_DIR.exists():
    wis_path = TABULAR_DIR / "data.csv"
    if wis_path.exists():
        df = pd.read_csv(wis_path)
        total_cases = len(df)
        malignant = int((df["diagnosis"] == "M").sum()) if "diagnosis" in df.columns else 0
        benign = total_cases - malignant
        col3.metric(get_translation(lang, "dashboard.wisconsin_cases"), total_cases)
        col4.metric(get_translation(lang, "dashboard.malignant_benign"), f"{malignant} / {benign}")
    else:
        col3.metric(get_translation(lang, "dashboard.wisconsin_cases"), get_translation(lang, "dashboard.no_data"))
        col4.metric(get_translation(lang, "dashboard.malignant_benign"), get_translation(lang, "dashboard.no_data"))
else:
    col3.metric(get_translation(lang, "dashboard.wisconsin_cases"), get_translation(lang, "dashboard.no_data_folder"))
    col4.metric(get_translation(lang, "dashboard.malignant_benign"), get_translation(lang, "dashboard.no_data_folder"))

st.markdown("---")
st.subheader(get_translation(lang, "dashboard.data_files"))

tab1, tab2 = st.tabs([get_translation(lang, "dashboard.google_drive"), get_translation(lang, "dashboard.local_backend")])

with tab1:
    if DATA_DIR.exists():
        data = []
        for f in csv_files:
            size_kb = f.stat().st_size / 1024
            data.append({
                get_translation(lang, "dashboard.model"): f.name,
                "Tamaño (KB)" if lang == "es" else "Size (KB)": f"{size_kb:.1f}"
            })
        # st.table en vez de st.dataframe: st.dataframe se renderiza como una
        # grilla interactiva sobre <canvas> (glide-data-grid) que toma sus
        # colores del tema nativo de Streamlit, no de nuestro CSS inyectado.
        # st.table es HTML real, así que sí respeta el tema claro/oscuro.
        st.table(pd.DataFrame(data))
    else:
        st.warning(f"{get_translation(lang, 'dashboard.path_not_found')}: `{DATA_DIR}`")

with tab2:
    local_dir = FALLBACK_MODELS_DIR.parent / "CSVFiles"
    if local_dir.exists():
        data = []
        for f in local_dir.glob("*.csv"):
            size_kb = f.stat().st_size / 1024
            data.append({
                get_translation(lang, "dashboard.model"): f.name,
                "Tamaño (KB)" if lang == "es" else "Size (KB)": f"{size_kb:.1f}"
            })
        st.table(pd.DataFrame(data))
    else:
        st.warning(f"{get_translation(lang, 'dashboard.path_not_found')}: `{local_dir}`")

st.subheader(get_translation(lang, "dashboard.trained_models"))
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
                get_translation(lang, "dashboard.type"): classify_model(f.name),
                get_translation(lang, "dashboard.model"): f.name,
                get_translation(lang, "dashboard.size_mb"): f"{size_mb:.2f}",
            })
        df = pd.DataFrame(data)
        st.table(df.sort_values(get_translation(lang, "dashboard.type")))

with st.expander(get_translation(lang, "dashboard.summary_by_type")):
    rows = []
    for cat_label, _, _ in MODEL_CATEGORIES:
        count = sum(1 for f in model_files if classify_model(f.name) == cat_label)
        if count > 0:
            rows.append({
                get_translation(lang, "dashboard.type"): cat_label,
                get_translation(lang, "dashboard.quantity"): count
            })
    if rows:
        st.table(pd.DataFrame(rows).set_index(get_translation(lang, "dashboard.type")))

st.markdown("---")
st.subheader(get_translation(lang, "dashboard.recommended_workflow"))
workflow_steps = get_translation(lang, "dashboard.workflow_steps")
st.markdown("\n".join([f"{i+1}. {step}" for i, step in enumerate(workflow_steps)]))