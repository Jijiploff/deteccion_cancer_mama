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
from modules.i18n import get_translation


lang = st.session_state.get("language", "es")


@st.cache_resource
def load_data():
    eda = BreastCancerEDA(DRIVE_BASE)
    eda.load_all_data()
    return eda


st.title(get_translation(lang, "training.title"))
st.markdown(get_translation(lang, "training.description"))

drive_ok = Path(DRIVE_BASE).exists()
if not drive_ok:
    st.warning(get_translation(lang, "training.drive_not_mounted", drive_base=DRIVE_BASE))
    st.stop()

try:
    eda = load_data()
except Exception as e:
    st.error(f"{get_translation(lang, 'training.error_loading_data')}: {e}")
    st.stop()

if eda.wisconsin_data is None:
    st.error(get_translation(lang, "training.wisconsin_not_available"))
    st.stop()

with st.spinner(get_translation(lang, "training.preparing_data")):
    X_train, X_test, y_train, y_test = prepare_wisconsin_data(
        eda.wisconsin_data, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

st.success(get_translation(lang, "training.data_ready", train_count=len(X_train), test_count=len(X_test), feature_count=X_train.shape[1]))

st.subheader(get_translation(lang, "training.model_config"))

models_to_train = st.multiselect(
    get_translation(lang, "training.select_models"),
    ["XGBoost", "Random Forest"],
    default=["XGBoost", "Random Forest"],
)

xgb_params = {}
rf_params = {}

with st.expander(get_translation(lang, "training.params_xgboost"), expanded="XGBoost" in models_to_train):
    col1, col2, col3 = st.columns(3)
    xgb_params["n_estimators"] = col1.number_input("n_estimators", 10, 500, 100, step=10, key="xgb_n_estimators")
    xgb_params["max_depth"] = col2.number_input("max_depth", 2, 20, 6, key="xgb_max_depth")
    xgb_params["learning_rate"] = col3.select_slider("learning_rate", [0.001, 0.01, 0.05, 0.1, 0.2, 0.3], 0.1, key="xgb_learning_rate")
    col4, col5 = st.columns(2)
    xgb_params["subsample"] = col4.select_slider("subsample", [0.4, 0.6, 0.8, 1.0], 0.8, key="xgb_subsample")
    xgb_params["colsample_bytree"] = col5.select_slider("colsample_bytree", [0.4, 0.6, 0.8, 1.0], 0.8, key="xgb_colsample_bytree")
    xgb_params["random_state"] = RANDOM_STATE
    xgb_params["eval_metric"] = "logloss"

with st.expander(get_translation(lang, "training.params_random_forest"), expanded="Random Forest" in models_to_train):
    col1, col2, col3 = st.columns(3)
    rf_params["n_estimators"] = col1.number_input("n_estimators", 10, 500, 100, step=10, key="rf_n_estimators")
    rf_params["max_depth"] = col2.number_input("max_depth", 2, 30, 6, key="rf_max_depth") or None
    rf_params["min_samples_split"] = col3.number_input("min_samples_split", 2, 20, 2, key="rf_min_samples_split")
    rf_params["random_state"] = RANDOM_STATE

if st.button(get_translation(lang, "training.start_training"), type="primary", use_container_width=True):
    if not models_to_train:
        st.warning(get_translation(lang, "training.select_at_least_one"))
        st.stop()

    results = {}
    models = {}
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, model_name in enumerate(models_to_train):
        status_text.info(get_translation(lang, "training.training", model_name=model_name))

        if model_name == "XGBoost":
            model, elapsed = train_xgboost(X_train, y_train, X_test, y_test, xgb_params)
        else:
            model, elapsed = train_random_forest(X_train, y_train, rf_params)

        metrics = evaluate_model(model, X_test, y_test)
        metrics["training_time_s"] = round(elapsed, 3)
        results[model_name] = metrics
        models[model_name] = model

        progress_bar.progress((i + 1) / len(models_to_train))

    status_text.success(get_translation(lang, "training.training_complete"))

    st.subheader(get_translation(lang, "training.results"))

    st.subheader(get_translation(lang, "training.comparison_table"))
    comparison_data = []
    for name, m in results.items():
        comparison_data.append({
            get_translation(lang, "training.metrics.model"): name,
            get_translation(lang, "training.metrics.accuracy"): f"{m['accuracy']:.4f}",
            get_translation(lang, "training.metrics.precision"): f"{m['precision']:.4f}",
            get_translation(lang, "training.metrics.recall"): f"{m['recall']:.4f}",
            get_translation(lang, "training.metrics.f1_score"): f"{m['f1']:.4f}",
            get_translation(lang, "training.metrics.auc_roc"): f"{m['auc']:.4f}",
            get_translation(lang, "training.metrics.time"): f"{m['training_time_s']:.3f}",
        })
    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)

    with st.expander(get_translation(lang, "training.interpret_metrics")):
        best_acc = max(results.items(), key=lambda x: x[1]["accuracy"])
        best_auc = max(results.items(), key=lambda x: x[1]["auc"])
        st.markdown(
            f"- **{get_translation(lang, 'training.best_accuracy')}:** {best_acc[0]} ({best_acc[1]['accuracy']:.4f})  \n"
            f"- **{get_translation(lang, 'training.best_auc')}:** {best_auc[0]} ({best_auc[1]['auc']:.4f})  \n"
            f"> {get_translation(lang, 'training.accuracy_explanation')}  \n"
            f"> {get_translation(lang, 'training.precision_explanation')}  \n"
            f"> {get_translation(lang, 'training.recall_explanation')}  \n"
            f"> {get_translation(lang, 'training.f1_explanation')}  \n"
            f"> {get_translation(lang, 'training.auc_explanation')}"
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
        with st.expander(get_translation(lang, "training.detail", model_name=name), expanded=True):
            cc1, cc2 = st.columns(2)
            with cc1:
                st.plotly_chart(plot_confusion_matrix(
                    m["confusion_matrix"], title=f"{name} - {get_translation(lang, 'training.confusion_matrix')}"
                ), use_container_width=True)
            with cc2:
                fi = plot_feature_importance(
                    models[name], X_train.columns, title=f"{name} - {get_translation(lang, 'training.feature_importance')}"
                )
                if fi:
                    st.plotly_chart(fi, use_container_width=True)

            cm = m["confusion_matrix"]
            st.info(
                f"**{get_translation(lang, 'training.true_positives')}:** {cm['tn']}  |  "
                f"**{get_translation(lang, 'training.true_negatives')}:** {cm['tp']}  |  "
                f"**{get_translation(lang, 'training.false_positives')}:** {cm['fp']}  |  "
                f"**{get_translation(lang, 'training.false_negatives')}:** {cm['fn']}"
            )

    with st.expander(get_translation(lang, "training.classification_report")):
        for name, m in results.items():
            st.markdown(f"**{name}**")
            st.json(m["classification_report"])

    st.subheader(get_translation(lang, "training.save_models"))
    save_cols = st.columns(len(models_to_train))
    for idx, name in enumerate(models_to_train):
        with save_cols[idx]:
            if st.button(get_translation(lang, "training.save_model", model_name=name), key=f"save_{name}"):
                params = xgb_params if name == "XGBoost" else rf_params
                model_path, meta_path = save_model(
                    models[name], name.lower().replace(" ", "_"),
                    RESULTS_DIR, MODELS_DIR, results[name], params,
                )
                st.success(get_translation(lang, "training.model_saved", model_name=name, model_path=model_path, meta_path=meta_path))
