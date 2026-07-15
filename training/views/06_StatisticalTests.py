from pathlib import Path

import streamlit as st

from config import DRIVE_BASE, RANDOM_STATE
from modules.eda import BreastCancerEDA
from modules.models import prepare_wisconsin_data, train_xgboost, train_random_forest, evaluate_model
from modules.statistical_tests import run_all_tests, plot_pvalue_heatmap
from modules.i18n import get_translation


lang = st.session_state.get("language", "es")


@st.cache_resource
def load_data():
    eda = BreastCancerEDA(DRIVE_BASE)
    eda.load_all_data()
    return eda


st.title(get_translation(lang, "statistical_tests.title"))
st.markdown(get_translation(lang, "statistical_tests.description"))

drive_ok = Path(DRIVE_BASE).exists()
if not drive_ok:
    st.warning(get_translation(lang, "statistical_tests.drive_not_mounted", drive_base=DRIVE_BASE))
    st.stop()

try:
    eda = load_data()
except Exception as e:
    st.error(f"{get_translation(lang, 'statistical_tests.error_loading_data')}: {e}")
    st.stop()

if eda.wisconsin_data is None:
    st.error(get_translation(lang, "statistical_tests.wisconsin_not_available"))
    st.stop()

with st.spinner(get_translation(lang, "statistical_tests.preparing_data")):
    X_train, X_test, y_train, y_test = prepare_wisconsin_data(
        eda.wisconsin_data, random_state=RANDOM_STATE
    )

st.success(get_translation(lang, "statistical_tests.data_ready", train_count=len(X_train), test_count=len(X_test)))

with st.spinner(get_translation(lang, "statistical_tests.training_reference")):
    xgb_model, _ = train_xgboost(X_train, y_train, X_test, y_test)
    rf_model, _ = train_random_forest(X_train, y_train)
    xgb_metrics = evaluate_model(xgb_model, X_test, y_test)
    rf_metrics = evaluate_model(rf_model, X_test, y_test)

models_data = {
    "XGBoost": {"y_pred": xgb_metrics["y_pred"], "y_proba": xgb_metrics["y_proba"]},
    "Random Forest": {"y_pred": rf_metrics["y_pred"], "y_proba": rf_metrics["y_proba"]},
}

st.info(get_translation(lang, "statistical_tests.reference_info"))

st.subheader(get_translation(lang, "statistical_tests.methodology"))

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"#### {get_translation(lang, 'statistical_tests.mcnemar')}")
    st.markdown(get_translation(lang, "statistical_tests.mcnemar_description"))
with col2:
    st.markdown(f"#### {get_translation(lang, 'statistical_tests.wilcoxon')}")
    st.markdown(get_translation(lang, "statistical_tests.wilcoxon_description"))

if st.button(get_translation(lang, "statistical_tests.run_tests"), type="primary", use_container_width=True):
    results_df = run_all_tests(models_data, y_test)

    st.success(get_translation(lang, "statistical_tests.tests_complete"))

    st.subheader(get_translation(lang, "statistical_tests.pairwise_results"))

    display_df = results_df[
        [get_translation(lang, "statistical_tests.model_a"),
         get_translation(lang, "statistical_tests.model_b"),
         get_translation(lang, "statistical_tests.mcnemar_pvalue"),
         get_translation(lang, "statistical_tests.mcnemar_interpretation"),
         get_translation(lang, "statistical_tests.wilcoxon_pvalue"),
         get_translation(lang, "statistical_tests.wilcoxon_interpretation")]
    ]

    styled = display_df.style.applymap(
        lambda v: "color: red; font-weight: bold" if isinstance(v, str) and get_translation(lang, "statistical_tests.significant") in v
        else ("color: green" if isinstance(v, str) and get_translation(lang, "statistical_tests.no_differences") in v else ""),
        subset=[get_translation(lang, "statistical_tests.mcnemar_interpretation"),
                get_translation(lang, "statistical_tests.wilcoxon_interpretation")],
    )
    st.dataframe(styled, use_container_width=True)

    st.subheader(get_translation(lang, "statistical_tests.heatmap"))
    st.plotly_chart(plot_pvalue_heatmap(results_df), use_container_width=True)

    st.subheader(get_translation(lang, "statistical_tests.general_interpretation"))
    sig_count = sum(
        1 for _, r in results_df.iterrows()
        if isinstance(r[get_translation(lang, "statistical_tests.mcnemar_pvalue")], (int, float))
        and r[get_translation(lang, "statistical_tests.mcnemar_pvalue")] < 0.05
    )
    total = len(results_df)

    if sig_count == 0:
        st.success(get_translation(lang, "statistical_tests.no_significant", total=total))
    elif sig_count < total:
        st.warning(get_translation(lang, "statistical_tests.some_significant", sig_count=sig_count, total=total))
    else:
        st.error(get_translation(lang, "statistical_tests.all_significant", total=total))

    with st.expander(get_translation(lang, "statistical_tests.how_to_interpret")):
        st.markdown(get_translation(lang, "statistical_tests.interpretation_guide"))
