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
from modules.i18n import get_translation


lang = st.session_state.get("language", "es")


@st.cache_resource
def load_data():
    eda = BreastCancerEDA(DRIVE_BASE)
    eda.load_all_data()
    return eda


st.title(get_translation(lang, "hyperparameter_tuning.title"))
st.markdown(get_translation(lang, "hyperparameter_tuning.description"))

drive_ok = Path(DRIVE_BASE).exists()
if not drive_ok:
    st.warning(get_translation(lang, "hyperparameter_tuning.drive_not_mounted", drive_base=DRIVE_BASE))
    st.stop()

try:
    eda = load_data()
except Exception as e:
    st.error(f"{get_translation(lang, 'hyperparameter_tuning.error_loading_data')}: {e}")
    st.stop()

if eda.wisconsin_data is None:
    st.error(get_translation(lang, "hyperparameter_tuning.wisconsin_not_available"))
    st.stop()

wis_df = eda.wisconsin_data.drop(["id", "Unnamed: 32"], axis=1, errors="ignore").dropna()
X = wis_df.drop("diagnosis", axis=1)
y = (wis_df["diagnosis"] == "M").astype(int)

st.success(get_translation(lang, "hyperparameter_tuning.data_ready", sample_count=X.shape[0], feature_count=X.shape[1]))

st.subheader(get_translation(lang, "hyperparameter_tuning.config"))

model_to_tune = st.selectbox(get_translation(lang, "hyperparameter_tuning.select_model"), ["XGBoost", "Random Forest"])

n_folds = st.number_input(get_translation(lang, "hyperparameter_tuning.cv_folds"), 3, 10, 5)

grid = XGBOOST_GRID if model_to_tune == "XGBoost" else RF_GRID

with st.expander(get_translation(lang, "hyperparameter_tuning.param_grid"), expanded=True):
    for param, values in grid.items():
        st.markdown(f"**{param}**: {values}")

total_combos = 1
for v in grid.values():
    total_combos *= len(v)
st.info(get_translation(lang, "hyperparameter_tuning.total_combinations", total_combos=total_combos, n_folds=n_folds, total_trainings=total_combos * n_folds))

if st.button(get_translation(lang, "hyperparameter_tuning.start_search"), type="primary", use_container_width=True):
    with st.spinner(get_translation(lang, "hyperparameter_tuning.searching", model_name=model_to_tune)):
        result = run_grid_search(
            model_to_tune, X, y, grid, n_folds=n_folds, random_state=RANDOM_STATE
        )

    st.success(get_translation(lang, "hyperparameter_tuning.search_complete", total_time=result['total_time_s'], total_combinations=result['total_combinations']))

    st.subheader(get_translation(lang, "hyperparameter_tuning.best_params"))
    st.dataframe(format_best_params_table(result), use_container_width=True)

    st.metric(get_translation(lang, "hyperparameter_tuning.best_auc"), f"{result['best_score']:.4f}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### {get_translation(lang, 'hyperparameter_tuning.best_config')}")
        st.json(result["best_params"])
    with col2:
        st.markdown(f"#### {get_translation(lang, 'hyperparameter_tuning.original_params')}")
        st.json(grid)

    st.subheader(get_translation(lang, "hyperparameter_tuning.results_visualization"))

    with st.expander(get_translation(lang, "hyperparameter_tuning.param_heatmaps")):
        param_pairs = []
        params = list(grid.keys())
        for i in range(len(params)):
            for j in range(i + 1, len(params)):
                param_pairs.append((params[i], params[j]))

        for px_param, py_param in param_pairs:
            fig = plot_tuning_heatmap(result, px_param, py_param)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    with st.expander(get_translation(lang, "hyperparameter_tuning.interpretation")):
        best = result["best_params"]
        params_list = "".join(f"- `{k}` = `{v}`  \n" for k, v in best.items())
        st.markdown(get_translation(lang, "hyperparameter_tuning.interpretation_text",
                                    model_name=model_to_tune, params_list=params_list,
                                    best_score=result['best_score']))

    st.subheader(get_translation(lang, "hyperparameter_tuning.apply_params"))
    st.info(get_translation(lang, "hyperparameter_tuning.apply_info"))
