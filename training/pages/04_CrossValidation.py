from pathlib import Path

import streamlit as st
import pandas as pd

from config import DRIVE_BASE, RANDOM_STATE
from modules.eda import BreastCancerEDA
from modules.cross_validation import (
    run_cross_validation,
    plot_cv_results,
    plot_cv_boxplot,
    format_cv_table,
)
from modules.models import prepare_wisconsin_data


@st.cache_resource
def load_data():
    eda = BreastCancerEDA(DRIVE_BASE)
    eda.load_all_data()
    return eda


st.title("🔁 Validación Cruzada (Cross-Validation)")
st.markdown(
    "Evalúa la robustez de los modelos usando **K-Fold Cross-Validation** estratificado.  \n"
    "El dataset se divide en K folds, entrenando en K-1 y validando en el fold restante, "
    "repitiendo K veces para obtener una estimación robusta del rendimiento."
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

X, y = None, None
with st.spinner("Preparando datos..."):
    X_train, X_test, y_train, y_test = prepare_wisconsin_data(
        eda.wisconsin_data, random_state=RANDOM_STATE
    )
    wis_df = eda.wisconsin_data.drop(["id", "Unnamed: 32"], axis=1, errors="ignore").dropna()
    X = wis_df.drop("diagnosis", axis=1)
    y = (wis_df["diagnosis"] == "M").astype(int)

st.success(f"Datos listos: {X.shape[0]} muestras, {X.shape[1]} características.")

st.subheader("⚙️ Configuración")

col1, col2 = st.columns(2)
n_splits = col1.number_input("Número de Folds (K)", 3, 10, 5)
models_to_cv = col2.multiselect(
    "Modelos",
    ["XGBoost", "Random Forest"],
    default=["XGBoost", "Random Forest"],
)

if st.button("🔁 Ejecutar Validación Cruzada", type="primary", use_container_width=True):
    if not models_to_cv:
        st.warning("Selecciona al menos un modelo.")
        st.stop()

    all_results = []
    progress_bar = st.progress(0)
    status = st.empty()

    for i, model_name in enumerate(models_to_cv):
        status.info(f"Ejecutando CV para {model_name} ({n_splits} folds)...")
        result = run_cross_validation(
            X, y, model_name, n_splits=n_splits, random_state=RANDOM_STATE
        )
        all_results.append(result)
        progress_bar.progress((i + 1) / len(models_to_cv))

    status.success("Validación Cruzada completada!")

    for cv in all_results:
        st.subheader(f"📊 {cv['model_name']} - Resultados por Fold")
        st.dataframe(format_cv_table(cv), use_container_width=True)
        st.plotly_chart(plot_cv_results(cv), use_container_width=True)

        st.info(
            f"**Accuracy:** {cv['mean_accuracy']:.4f} ± {cv['std_accuracy']:.4f}  |  "
            f"**AUC:** {cv['mean_auc']:.4f} ± {cv['std_auc']:.4f}  |  "
            f"**Rango Accuracy:** {cv['min_accuracy']:.4f} – {cv['max_accuracy']:.4f}  |  "
            f"**Tiempo total:** {cv['total_time_s']:.2f}s"
        )

        with st.expander("📖 Interpretación"):
            std = cv["std_accuracy"]
            if std < 0.01:
                estab = "muy estable"
            elif std < 0.03:
                estab = "estable"
            else:
                estab = "presenta cierta variabilidad"
            st.markdown(
                f"El modelo **{cv['model_name']}** muestra un accuracy promedio de "
                f"**{cv['mean_accuracy']:.4f}** con una desviación estándar de **{std:.4f}**, "
                f"lo que indica que el modelo es **{estab}** a través de los {n_splits} folds.  \n\n"
                f"El AUC promedio de **{cv['mean_auc']:.4f}** confirma una buena capacidad "
                f"de discriminación entre clases malignas y benignas."
            )

    if len(all_results) > 1:
        st.subheader("📈 Comparación entre Modelos")
        st.plotly_chart(plot_cv_boxplot(all_results), use_container_width=True)
