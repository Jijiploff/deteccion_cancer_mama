from pathlib import Path

import streamlit as st
import pandas as pd

from config import DRIVE_BASE, RANDOM_STATE
from modules.eda import BreastCancerEDA
from modules.hyperparameter_tuning import (
    run_grid_search,
    plot_tuning_heatmap,
    format_best_params_table,
    XGBOOST_GRID,
    RF_GRID,
)


@st.cache_resource
def load_data():
    eda = BreastCancerEDA(DRIVE_BASE)
    eda.load_all_data()
    return eda


st.title("⚙️ Búsqueda de Hiperparámetros (Tuning)")
st.markdown(
    "Encuentra la mejor combinación de hiperparámetros usando **GridSearchCV** "
    "con validación cruzada.  \n"
    "Esto evalúa todas las combinaciones posibles y selecciona la de mayor rendimiento (AUC)."
)

drive_ok = Path(DRIVE_BASE).exists()
if not drive_ok:
    st.warning(f"⚠️ Google Drive no está montado en `{DRIVE_BASE}`.")
    st.stop()

try:
    eda = load_data()
except Exception as e:
    st.error(f"Error cargando datos: {e}")
    st.stop()

if eda.wisconsin_data is None:
    st.error("Dataset Wisconsin no disponible.")
    st.stop()

wis_df = eda.wisconsin_data.drop(["id", "Unnamed: 32"], axis=1, errors="ignore").dropna()
X = wis_df.drop("diagnosis", axis=1)
y = (wis_df["diagnosis"] == "M").astype(int)

st.success(f"Datos listos: {X.shape[0]} muestras, {X.shape[1]} características.")

st.subheader("⚙️ Configuración")

model_to_tune = st.selectbox("Seleccionar modelo", ["XGBoost", "Random Forest"])

n_folds = st.number_input("Folds para validación cruzada", 3, 10, 5)

grid = XGBOOST_GRID if model_to_tune == "XGBoost" else RF_GRID

with st.expander("📋 Grid de Parámetros a Evaluar", expanded=True):
    for param, values in grid.items():
        st.markdown(f"**{param}**: {values}")

total_combos = 1
for v in grid.values():
    total_combos *= len(v)
st.info(f"Total de combinaciones: **{total_combos}** (cada una con {n_folds} folds = {total_combos * n_folds} entrenamientos)")

if st.button("🚀 Iniciar Búsqueda", type="primary", use_container_width=True):
    with st.spinner(f"Ejecutando GridSearch para {model_to_tune}... esto puede tomar varios minutos."):
        result = run_grid_search(
            model_to_tune, X, y, grid, n_folds=n_folds, random_state=RANDOM_STATE
        )

    st.success(
        f"Búsqueda completada en {result['total_time_s']:.2f}s. "
        f"Se evaluaron {result['total_combinations']} combinaciones."
    )

    st.subheader("🏆 Mejores Parámetros Encontrados")
    st.dataframe(format_best_params_table(result), use_container_width=True)

    st.metric("Mejor AUC (CV)", f"{result['best_score']:.4f}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Mejor configuración")
        st.json(result["best_params"])
    with col2:
        st.markdown("#### Parámetros originales")
        st.json(grid)

    st.subheader("📊 Visualización de Resultados")

    with st.expander("Heatmaps de Parámetros"):
        param_pairs = []
        params = list(grid.keys())
        for i in range(len(params)):
            for j in range(i + 1, len(params)):
                param_pairs.append((params[i], params[j]))

        for px_param, py_param in param_pairs:
            fig = plot_tuning_heatmap(result, px_param, py_param)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    with st.expander("📖 Interpretación"):
        best = result["best_params"]
        st.markdown(
            f"La mejor configuración para **{model_to_tune}** fue:  \n"
            + "".join(f"- `{k}` = `{v}`  \n" for k, v in best.items()) +
            f"\nCon un AUC promedio de validación cruzada de **{result['best_score']:.4f}**.  \n\n"
            "> * Nota: Estos parámetros pueden ajustarse manualmente en la sección de Entrenamiento "
            "para refinar aún más el modelo."
        )

    st.subheader("💾 Aplicar Mejores Parámetros")
    st.info(
        "Copia los mejores parámetros de arriba y úsalos en la sección **🧠 Entrenamiento** "
        "para entrenar el modelo final con la configuración óptima."
    )
