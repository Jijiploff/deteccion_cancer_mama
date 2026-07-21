import json

import streamlit as st
import pandas as pd

from config import JSON_RESULTS_PATH
from modules.i18n import get_translation


lang = st.session_state.get("language", "es")


def load_json_results():
    if JSON_RESULTS_PATH.exists():
        with open(JSON_RESULTS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return None


def format_model_name(key: str) -> str:
    names = {
        "tabular_xgboost": "XGBoost (Wisconsin)",
        "tabular_rf": "Random Forest (Wisconsin)",
        "cnn_efficientnet": "CNN (EfficientNet)",
        "hybrid_cnn_rf": "Hybrid CNN-RF",
        "hybrid_cnn_xgb": "Hybrid CNN-XGBoost",
    }
    return names.get(key, key)


st.title("⚙️ Hiperparámetros — Resultados Precomputados")
st.markdown(
    "Mejores hiperparámetros encontrados mediante **GridSearchCV** (XGBoost) y "
    "**RandomizedSearchCV** (Random Forest) en Google Colab.  \n"
    "No se requiere re-ejecutar la búsqueda en la nube."
)

data = load_json_results()

if not data:
    st.warning("No se encontró el archivo de resultados.")
    st.stop()

config = data.get("config", {})
best_params = data.get("fase2_modelado", {}).get("best_params_tuning", {})
metricas = data.get("fase2_modelado", {}).get("metricas_test", {})

if not best_params:
    st.info("No hay hiperparámetros guardados en el archivo de resultados.")
    st.stop()

# Grid original usado
st.subheader("📋 Grid de Búsqueda Utilizado")

grid_info = {
    "XGBoost (GridSearchCV)": config.get("XGB_PARAM_GRID", {}),
    "Random Forest (RandomizedSearchCV)": config.get("RF_PARAM_DIST", {}),
}

for model_name, grid in grid_info.items():
    with st.expander(f"**{model_name}**"):
        grid_df = pd.DataFrame(
            [{"Parámetro": k, "Valores explorados": str(v)} for k, v in grid.items()]
        )
        st.table(grid_df)

# Mejores parámetros encontrados
st.subheader("🏆 Mejores Parámetros Encontrados")

for model_key, params in best_params.items():
    display_name = format_model_name(model_key)

    with st.container():
        st.markdown(f"**{display_name}**")

        params_df = pd.DataFrame(
            [{"Parámetro": k, "Valor óptimo": str(v)} for k, v in params.items()]
        )
        st.table(params_df)

        # Mostrar métricas con estos parámetros
        m = metricas.get(model_key, {})
        if m:
            st.info(
                f"Métricas en test con esta configuración:\n\n"
                f"Accuracy: **{m['accuracy']:.4f}** | "
                f"Precision: **{m['precision']:.4f}** | "
                f"Recall: **{m['recall']:.4f}** | "
                f"F1: **{m['f1']:.4f}** | "
                f"AUC: **{m['auc']:.4f}**"
            )

    st.divider()

# Interpretación
st.subheader("📖 Interpretación")
st.markdown(
    "La búsqueda de hiperparámetros se realizó con validación cruzada interna (CV folds = "
    f"**{config.get('TUNING_CV', 3)}**) para encontrar la configuración que maximiza el AUC.  \n\n"
    "Los parámetros óptimos encontrados son específicos del dataset Wisconsin y pueden "
    "variar si se aplican a otros datos."
)
