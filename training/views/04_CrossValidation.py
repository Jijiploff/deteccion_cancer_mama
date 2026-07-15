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
from modules.i18n import get_translation


lang = st.session_state.get("language", "es")


@st.cache_resource
def load_data():
    eda = BreastCancerEDA(DRIVE_BASE)
    eda.load_all_data()
    return eda


st.title(get_translation(lang, "cross_validation.title"))
st.markdown(get_translation(lang, "cross_validation.description"))

drive_ok = Path(DRIVE_BASE).exists()
if not drive_ok:
    st.warning(get_translation(lang, "cross_validation.drive_not_mounted", drive_base=DRIVE_BASE))
    st.stop()

try:
    eda = load_data()
except Exception as e:
    st.error(f"{get_translation(lang, 'cross_validation.error_loading_data')}: {e}")
    st.stop()

if eda.wisconsin_data is None:
    st.error(get_translation(lang, "cross_validation.wisconsin_not_available"))
    st.stop()

X, y = None, None
with st.spinner(get_translation(lang, "cross_validation.preparing_data")):
    X_train, X_test, y_train, y_test = prepare_wisconsin_data(
        eda.wisconsin_data, random_state=RANDOM_STATE
    )
    wis_df = eda.wisconsin_data.drop(["id", "Unnamed: 32"], axis=1, errors="ignore").dropna()
    X = wis_df.drop("diagnosis", axis=1)
    y = (wis_df["diagnosis"] == "M").astype(int)

st.success(get_translation(lang, "cross_validation.data_ready", sample_count=X.shape[0], feature_count=X.shape[1]))

st.subheader(get_translation(lang, "cross_validation.config"))

col1, col2 = st.columns(2)
n_splits = col1.number_input(get_translation(lang, "cross_validation.n_folds"), 3, 10, 5)
models_to_cv = col2.multiselect(
    get_translation(lang, "cross_validation.models"),
    ["XGBoost", "Random Forest"],
    default=["XGBoost", "Random Forest"],
)

if st.button(get_translation(lang, "cross_validation.run_cv"), type="primary", use_container_width=True):
    if not models_to_cv:
        st.warning(get_translation(lang, "cross_validation.select_at_least_one"))
        st.stop()

    all_results = []
    progress_bar = st.progress(0)
    status = st.empty()

    for i, model_name in enumerate(models_to_cv):
        status.info(get_translation(lang, "cross_validation.running_cv", model_name=model_name, n_splits=n_splits))
        result = run_cross_validation(
            X, y, model_name, n_splits=n_splits, random_state=RANDOM_STATE
        )
        all_results.append(result)
        progress_bar.progress((i + 1) / len(models_to_cv))

    status.success(get_translation(lang, "cross_validation.cv_complete"))

    for cv in all_results:
        st.subheader(f"📊 {cv['model_name']} - {get_translation(lang, 'cross_validation.results_by_fold')}")
        st.dataframe(format_cv_table(cv), use_container_width=True)
        st.plotly_chart(plot_cv_results(cv), use_container_width=True)

        st.info(
            f"**{get_translation(lang, 'cross_validation.accuracy')}:** {cv['mean_accuracy']:.4f} ± {cv['std_accuracy']:.4f}  |  "
            f"**{get_translation(lang, 'cross_validation.auc')}:** {cv['mean_auc']:.4f} ± {cv['std_auc']:.4f}  |  "
            f"**{get_translation(lang, 'cross_validation.accuracy_range')}:** {cv['min_accuracy']:.4f} – {cv['max_accuracy']:.4f}  |  "
            f"**{get_translation(lang, 'cross_validation.total_time')}:** {cv['total_time_s']:.2f}s"
        )

        with st.expander(get_translation(lang, "cross_validation.interpretation")):
            std = cv["std_accuracy"]
            if std < 0.01:
                estab = get_translation(lang, "cross_validation.very_stable")
            elif std < 0.03:
                estab = get_translation(lang, "cross_validation.stable")
            else:
                estab = get_translation(lang, "cross_validation.variable")
            st.markdown(get_translation(lang, "cross_validation.interpretation_text",
                                        model_name=cv['model_name'], mean_accuracy=cv['mean_accuracy'],
                                        std_accuracy=cv['std_accuracy'], stability=estab, n_splits=n_splits,
                                        mean_auc=cv['mean_auc']))

    if len(all_results) > 1:
        st.subheader(get_translation(lang, "cross_validation.comparison"))
        st.plotly_chart(plot_cv_boxplot(all_results), use_container_width=True)
