import json
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

from config import MODELS_DIR, JSON_RESULTS_PATH, RESULTS_DIR
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


def format_model_type(key: str) -> str:
    types = {
        "tabular_xgboost": "Tabular",
        "tabular_rf": "Tabular",
        "cnn_efficientnet": "CNN / Imagen",
        "hybrid_cnn_rf": "Híbrido",
        "hybrid_cnn_xgb": "Híbrido",
    }
    return types.get(key, "Otro")


st.title("📦 Catálogo de Modelos Entrenados")
st.markdown("Todos los modelos fueron entrenados en **Google Colab con GPU**. Aquí se listan sus métricas y archivos disponibles.")

data = load_json_results()

# ── Modelos desde el JSON ─────────────────────────────────
if data and "fase2_modelado" in data:
    metricas = data["fase2_modelado"]["metricas_test"]
    cv_data = data.get("validacion_cruzada", {})
    ranking = data.get("ranking_modelos", {})

    rows = []
    for model_key, m in metricas.items():
        cv = cv_data.get(model_key, {})
        rows.append({
            "Modelo": format_model_name(model_key),
            "Tipo": format_model_type(model_key),
            "Accuracy": m["accuracy"],
            "Precision": m["precision"],
            "Recall": m["recall"],
            "F1-Score": m["f1"],
            "AUC-ROC": m["auc"],
            "CV Accuracy (media)": cv.get("accuracy_media", None),
            "CV AUC (media)": cv.get("auc_media", None),
        })

    df = pd.DataFrame(rows)

    st.subheader("📊 Métricas en Test")
    display_df = df.copy()
    for col in ["Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC", "CV Accuracy (media)", "CV AUC (media)"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.4f}" if isinstance(x, (int, float)) else "-")
    st.dataframe(display_df, use_container_width=True)

    # Gráfico comparativo
    chart_df = df.melt(
        id_vars=["Modelo", "Tipo"],
        value_vars=["Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"],
        var_name="Métrica",
        value_name="Valor",
    )
    fig = px.bar(
        chart_df,
        x="Métrica",
        y="Valor",
        color="Modelo",
        barmode="group",
        text_auto=".3f",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(height=450, yaxis_range=[0, 1.05], margin=dict(t=20))
    fig.update_traces(textposition="outside", textfont_size=9)
    st.plotly_chart(fig, use_container_width=True)

    # Ranking
    if ranking and "tabla" in ranking:
        st.subheader("🏆 Ranking de Modelos")
        rank_df = pd.DataFrame(ranking["tabla"])
        display_rank = rank_df[
            ["Puesto", "Modelo", "accuracy", "precision", "recall", "f1", "auc", "Score compuesto"]
        ].copy()
        for col in ["accuracy", "precision", "recall", "f1", "auc", "Score compuesto"]:
            display_rank[col] = display_rank[col].apply(lambda x: f"{x:.4f}")
        st.dataframe(display_rank, use_container_width=True)

        mejor = ranking.get("mejor_modelo", "")
        if mejor:
            st.success(f"🏆 **Mejor modelo general: {format_model_name(mejor)}**")

    # Matrices de confusión (tabla manual)
    st.subheader("📋 Matrices de Confusión")
    for model_key, m in metricas.items():
        cm = m.get("confusion_matrix", {})
        if cm:
            st.markdown(f"**{format_model_name(model_key)}**")
            cm_df = pd.DataFrame(
                [[cm.get("tn", 0), cm.get("fp", 0)], [cm.get("fn", 0), cm.get("tp", 0)]],
                index=["Real: BENIGN", "Real: MALIGNANT"],
                columns=["Pred: BENIGN", "Pred: MALIGNANT"],
            )
            st.dataframe(cm_df, use_container_width=True)

else:
    st.info("No se encontraron métricas de modelos entrenados en el archivo de resultados.")

# ── Archivos de modelo en disco ──────────────────────────
st.divider()
st.subheader("💾 Archivos de Modelo")

if data and "archivos_modelo_en_disco" in data:
    archivos_rows = []
    for model_key, path in data["archivos_modelo_en_disco"].items():
        p = Path(path)
        archivos_rows.append({
            "Modelo": format_model_name(model_key),
            "Archivo": p.name,
            "Ruta original": str(path),
        })
    st.table(pd.DataFrame(archivos_rows))

# Modelos descargados localmente
local_models = list(MODELS_DIR.glob("*")) if MODELS_DIR.exists() else []
if local_models:
    local_rows = []
    for f in sorted(local_models, key=lambda x: x.suffix):
        size_mb = f.stat().st_size / (1024 * 1024)
        local_rows.append({
            "Archivo": f.name,
            "Tamaño (MB)": f"{size_mb:.2f}",
        })
    st.markdown("**Modelos locales descargados:**")
    st.table(pd.DataFrame(local_rows))
else:
    st.info(f"No hay modelos descargados localmente en `{MODELS_DIR}`. Los modelos se descargarán desde HuggingFace Hub al configurar el repo.")
