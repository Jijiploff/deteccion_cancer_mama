from pathlib import Path

import streamlit as st
import pandas as pd

from config import DRIVE_BASE, TABULAR_DIR, RESULTS_DIR, MODELS_DIR, RANDOM_STATE, TEST_SIZE
from modules.eda import BreastCancerEDA
from modules.models import (
    prepare_wisconsin_data,
    train_xgboost,
    train_random_forest,
    evaluate_model,
    plot_confusion_matrix,
    plot_roc_curve,
    plot_feature_importance,
    plot_metrics_comparison,
    save_model,
)


@st.cache_resource
def load_data():
    eda = BreastCancerEDA(DRIVE_BASE)
    eda.load_all_data()
    return eda


st.title("🧠 Entrenamiento de Modelos")
st.markdown(
    "Entrena modelos clásicos de clasificación con los datos tabulares de Wisconsin.  \n"
    "> ⚡ Para entrenamiento de modelos CNN (EfficientNet) o Ensemble Híbrido, usa Google Colab."
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

with st.spinner("Preparando datos..."):
    X_train, X_test, y_train, y_test = prepare_wisconsin_data(
        eda.wisconsin_data, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

st.success(f"Datos listos: {len(X_train)} train, {len(X_test)} test, {X_train.shape[1]} características.")

st.subheader("⚙️ Configuración de Modelos")

models_to_train = st.multiselect(
    "Seleccionar modelos a entrenar",
    ["XGBoost", "Random Forest"],
    default=["XGBoost", "Random Forest"],
)

xgb_params = {}
rf_params = {}

with st.expander("Parámetros - XGBoost", expanded="XGBoost" in models_to_train):
    col1, col2, col3 = st.columns(3)
    xgb_params["n_estimators"] = col1.number_input("n_estimators", 10, 500, 100, step=10)
    xgb_params["max_depth"] = col2.number_input("max_depth", 2, 20, 6)
    xgb_params["learning_rate"] = col3.select_slider("learning_rate", [0.001, 0.01, 0.05, 0.1, 0.2, 0.3], 0.1)
    col4, col5 = st.columns(2)
    xgb_params["subsample"] = col4.select_slider("subsample", [0.4, 0.6, 0.8, 1.0], 0.8)
    xgb_params["colsample_bytree"] = col5.select_slider("colsample_bytree", [0.4, 0.6, 0.8, 1.0], 0.8)
    xgb_params["random_state"] = RANDOM_STATE
    xgb_params["eval_metric"] = "logloss"

with st.expander("Parámetros - Random Forest", expanded="Random Forest" in models_to_train):
    col1, col2, col3 = st.columns(3)
    rf_params["n_estimators"] = col1.number_input("n_estimators", 10, 500, 100, step=10)
    rf_params["max_depth"] = col2.number_input("max_depth", 2, 30, 6) or None
    rf_params["min_samples_split"] = col3.number_input("min_samples_split", 2, 20, 2)
    rf_params["random_state"] = RANDOM_STATE

if st.button("🚀 Iniciar Entrenamiento", type="primary", use_container_width=True):
    if not models_to_train:
        st.warning("Selecciona al menos un modelo.")
        st.stop()

    results = {}
    models = {}
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, model_name in enumerate(models_to_train):
        status_text.info(f"Entrenando {model_name}...")

        if model_name == "XGBoost":
            model, elapsed = train_xgboost(X_train, y_train, X_test, y_test, xgb_params)
        else:
            model, elapsed = train_random_forest(X_train, y_train, rf_params)

        metrics = evaluate_model(model, X_test, y_test)
        metrics["training_time_s"] = round(elapsed, 3)
        results[model_name] = metrics
        models[model_name] = model

        progress_bar.progress((i + 1) / len(models_to_train))

    status_text.success("Entrenamiento completado!")

    st.subheader("📊 Resultados")

    st.subheader("Tabla Comparativa de Métricas")
    comparison_data = []
    for name, m in results.items():
        comparison_data.append({
            "Modelo": name,
            "Accuracy": f"{m['accuracy']:.4f}",
            "Precision": f"{m['precision']:.4f}",
            "Recall": f"{m['recall']:.4f}",
            "F1-Score": f"{m['f1']:.4f}",
            "AUC-ROC": f"{m['auc']:.4f}",
            "Tiempo (s)": f"{m['training_time_s']:.3f}",
        })
    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)

    with st.expander("📖 Interpretación de Métricas"):
        best_acc = max(results.items(), key=lambda x: x[1]["accuracy"])
        best_auc = max(results.items(), key=lambda x: x[1]["auc"])
        st.markdown(
            f"- **Mejor Accuracy:** {best_acc[0]} ({best_acc[1]['accuracy']:.4f})  \n"
            f"- **Mejor AUC-ROC:** {best_auc[0]} ({best_auc[1]['auc']:.4f})  \n"
            "> *Accuracy*: proporción de predicciones correctas sobre el total.  \n"
            "> *Precision*: de los clasificados como MALIGNANT, cuántos realmente lo son.  \n"
            "> *Recall*: de los MALIGNANT reales, cuántos fueron detectados.  \n"
            "> *F1-Score*: media armónica de precisión y recall.  \n"
            "> *AUC-ROC*: capacidad de discriminación entre clases (1 = perfecto)."
        )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_metrics_comparison(results), use_container_width=True)

    roc_data = {}
    for name, m in results.items():
        roc_data[name] = m["y_proba"]
    with col2:
        st.plotly_chart(plot_roc_curve(y_test, roc_data), use_container_width=True)

    for name, m in results.items():
        with st.expander(f"📉 {name} - Detalle", expanded=True):
            cc1, cc2 = st.columns(2)
            with cc1:
                st.plotly_chart(plot_confusion_matrix(
                    m["confusion_matrix"], title=f"{name} - Matriz de Confusión"
                ), use_container_width=True)
            with cc2:
                fi = plot_feature_importance(
                    models[name], X_train.columns, title=f"{name} - Importancia"
                )
                if fi:
                    st.plotly_chart(fi, use_container_width=True)

            cm = m["confusion_matrix"]
            st.info(
                f"**VP (BENIGN correctos):** {cm['tn']}  |  "
                f"**VN (MALIGNANT correctos):** {cm['tp']}  |  "
                f"**FP:** {cm['fp']}  |  "
                f"**FN:** {cm['fn']}"
            )

    with st.expander("📄 Reporte de Clasificación Detallado"):
        for name, m in results.items():
            st.markdown(f"**{name}**")
            st.json(m["classification_report"])

    st.subheader("💾 Guardar Modelos")
    save_cols = st.columns(len(models_to_train))
    for idx, name in enumerate(models_to_train):
        with save_cols[idx]:
            if st.button(f"💾 Guardar {name}", key=f"save_{name}"):
                params = xgb_params if name == "XGBoost" else rf_params
                model_path, meta_path = save_model(
                    models[name], name.lower().replace(" ", "_"),
                    RESULTS_DIR, MODELS_DIR, results[name], params,
                )
                st.success(f"{name} guardado:\n- {model_path}\n- {meta_path}")
