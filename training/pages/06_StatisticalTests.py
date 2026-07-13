from pathlib import Path

import streamlit as st

from config import DRIVE_BASE, RANDOM_STATE
from modules.eda import BreastCancerEDA
from modules.models import prepare_wisconsin_data, train_xgboost, train_random_forest, evaluate_model
from modules.statistical_tests import run_all_tests, plot_pvalue_heatmap


@st.cache_resource
def load_data():
    eda = BreastCancerEDA(DRIVE_BASE)
    eda.load_all_data()
    return eda


st.title("📈 Pruebas Estadísticas")
st.markdown(
    "Valida si las diferencias entre modelos son **estadísticamente significativas** "
    "usando pruebas robustas.  \n"
    "Esto permite determinar si un modelo realmente supera a otro o si las diferencias "
    "son atribuibles al azar."
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

with st.spinner("Preparando datos y entrenando modelos..."):
    X_train, X_test, y_train, y_test = prepare_wisconsin_data(
        eda.wisconsin_data, random_state=RANDOM_STATE
    )

st.success(f"Datos listos: {len(X_train)} train, {len(X_test)} test.")

with st.spinner("Entrenando modelos de referencia..."):
    xgb_model, _ = train_xgboost(X_train, y_train, X_test, y_test)
    rf_model, _ = train_random_forest(X_train, y_train)
    xgb_metrics = evaluate_model(xgb_model, X_test, y_test)
    rf_metrics = evaluate_model(rf_model, X_test, y_test)

models_data = {
    "XGBoost": {"y_pred": xgb_metrics["y_pred"], "y_proba": xgb_metrics["y_proba"]},
    "Random Forest": {"y_pred": rf_metrics["y_pred"], "y_proba": rf_metrics["y_proba"]},
}

st.info(
    "Se entrenaron modelos de referencia para realizar las comparaciones. "
    "Puedes ajustar los parámetros en la sección de Entrenamiento y volver aquí."
)

st.subheader("🔬 Metodología")

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        "#### Prueba de McNemar\n"
        "Compara las **predicciones categóricas** de dos modelos.  \n"
        "Evalúa si la proporción de aciertos/errores entre ambos "
        "es significativamente diferente.\n"
        "* **H0**: Los modelos tienen la misma tasa de error.\n"
        "* Estadístico: χ² (chi-cuadrado)"
    )
with col2:
    st.markdown(
        "#### Prueba de Wilcoxon\n"
        "Compara las **probabilidades predichas** de dos modelos.  \n"
        "Es una prueba no paramétrica que no asume normalidad.\n"
        "* **H0**: Las distribuciones de probabilidad son iguales.\n"
        "* Estadístico: W (rango firmado)"
    )

if st.button("📊 Ejecutar Pruebas Estadísticas", type="primary", use_container_width=True):
    results_df = run_all_tests(models_data, y_test)

    st.success("Pruebas ejecutadas!")

    st.subheader("📋 Resultados de Comparaciones por Pares")

    display_df = results_df[["Modelo A", "Modelo B", "McNemar p-valor", "McNemar Interpretación",
                              "Wilcoxon p-valor", "Wilcoxon Interpretación"]]

    styled = display_df.style.applymap(
        lambda v: "color: red; font-weight: bold" if isinstance(v, str) and "significativas" in v
        else ("color: green" if isinstance(v, str) and "Sin diferencias" in v else ""),
        subset=["McNemar Interpretación", "Wilcoxon Interpretación"],
    )
    st.dataframe(styled, use_container_width=True)

    st.subheader("📈 Mapa de Calor - p-valores (McNemar)")
    st.plotly_chart(plot_pvalue_heatmap(results_df), use_container_width=True)

    st.subheader("📖 Interpretación General")
    sig_count = sum(
        1 for _, r in results_df.iterrows()
        if isinstance(r["McNemar p-valor"], (int, float))
        and r["McNemar p-valor"] < 0.05
    )
    total = len(results_df)

    if sig_count == 0:
        st.success(
            f"Ninguna de las {total} comparaciones mostró diferencias significativas (p < 0.05). "
            "Esto sugiere que los modelos tienen rendimiento comparable."
        )
    elif sig_count < total:
        st.warning(
            f"{sig_count} de {total} comparaciones mostraron diferencias significativas. "
            "Algunos modelos superan a otros estadísticamente."
        )
    else:
        st.error(
            f"Todas las {total} comparaciones mostraron diferencias significativas. "
            "Los modelos tienen rendimientos distintos."
        )

    with st.expander("ℹ️ ¿Cómo interpretar estos resultados?"):
        st.markdown(
            """
        * **p < 0.05**: Hay evidencia estadística para rechazar H0 → los modelos son diferentes.
        * **p ≥ 0.05**: No hay suficiente evidencia → los modelos se comportan de forma similar.
        * Un p-valor alto **no significa** que los modelos sean idénticos, solo que no podemos
          demostrar que sean diferentes con los datos disponibles.
        * La prueba de McNemar es más sensible a diferencias en clasificación binaria,
          mientras que Wilcoxon considera la magnitud de las probabilidades.
        """
        )
