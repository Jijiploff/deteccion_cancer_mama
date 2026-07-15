from pathlib import Path

import streamlit as st

from config import DRIVE_BASE
from modules.eda import BreastCancerEDA
from modules.i18n import get_translation


lang = st.session_state.get("language", "es")


@st.cache_resource
def load_eda(base_path: str) -> BreastCancerEDA:
    eda = BreastCancerEDA(base_path)
    eda.load_all_data()
    return eda


st.title(get_translation(lang, "eda.title"))
st.markdown(
    f"**{get_translation(lang, 'dashboard.base_path')}:** `{DRIVE_BASE}`  \n"
    f"{get_translation(lang, 'eda.description')}"
)

drive_ok = Path(DRIVE_BASE).exists()
if not drive_ok:
    st.warning(get_translation(lang, "eda.drive_not_mounted"))
    st.stop()

try:
    eda = load_eda(DRIVE_BASE)
except Exception as e:
    st.error(f"{get_translation(lang, 'eda.error_loading_data')}: {e}")
    st.stop()

summary = eda.get_data_summary()

col1, col2, col3, col4 = st.columns(4)
col1.metric(get_translation(lang, "eda.calcificaciones"), summary["calcificaciones"])
col2.metric(get_translation(lang, "eda.masses"), summary["masas"])
col3.metric(get_translation(lang, "eda.metadata"), summary["metadatos"])
col4.metric(get_translation(lang, "eda.wisconsin_tabular"), summary["wisconsin"])

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    get_translation(lang, "eda.tabs.summary"),
    get_translation(lang, "eda.tabs.distributions"),
    get_translation(lang, "eda.tabs.correlations"),
    get_translation(lang, "eda.tabs.features"),
    get_translation(lang, "eda.tabs.raw_data"),
])

with tab1:
    st.subheader(get_translation(lang, "eda.dataset_summary"))

    st.markdown(f"#### {get_translation(lang, 'eda.cbis_ddsm_calc')}")
    if eda.calc_all is not None:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{get_translation(lang, 'eda.total_cases')}:** {len(eda.calc_all)}")
            st.markdown(f"**{get_translation(lang, 'eda.columns')}:** {list(eda.calc_all.columns)}")
        with c2:
            st.dataframe(eda.calc_all.head(5), use_container_width=True)

    st.markdown(f"#### {get_translation(lang, 'eda.cbis_ddsm_mass')}")
    if eda.mass_all is not None:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{get_translation(lang, 'eda.total_cases')}:** {len(eda.mass_all)}")
            st.markdown(f"**{get_translation(lang, 'eda.columns')}:** {list(eda.mass_all.columns)}")
        with c2:
            st.dataframe(eda.mass_all.head(5), use_container_width=True)

    st.markdown(f"#### {get_translation(lang, 'eda.wisconsin_breast_cancer')}")
    if eda.wisconsin_data is not None:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{get_translation(lang, 'eda.total_cases')}:** {len(eda.wisconsin_data)}")
            st.markdown(f"**{get_translation(lang, 'eda.columns')}:** {list(eda.wisconsin_data.columns)}")
        with c2:
            st.dataframe(eda.wisconsin_data.head(5), use_container_width=True)

    mapping = eda.get_image_mapping_stats()
    if mapping["series_en_meta"] > 0:
        st.markdown(f"#### {get_translation(lang, 'eda.image_mapping')}")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric(get_translation(lang, "eda.series_in_meta"), mapping["series_en_meta"])
        mc2.metric(get_translation(lang, "eda.image_folders"), mapping["carpetas_imagenes"])
        mc3.metric(get_translation(lang, "eda.matches"), mapping["coincidencias"])

    st.subheader(get_translation(lang, "eda.descriptive_stats"))
    try:
        st.dataframe(eda.get_wisconsin_descriptive_stats(), use_container_width=True)
    except Exception:
        st.info(get_translation(lang, "eda.not_available"))

with tab2:
    st.subheader(get_translation(lang, "eda.pathology_distribution"))
    st.plotly_chart(eda.plot_pathology_distribution(), use_container_width=True)

    st.subheader(get_translation(lang, "eda.birads_distribution"))
    st.plotly_chart(eda.plot_birads_distribution(), use_container_width=True)

    st.subheader(get_translation(lang, "eda.subtlety_distribution"))
    st.plotly_chart(eda.plot_subtlety_distribution(), use_container_width=True)

    st.subheader(get_translation(lang, "eda.stats_by_class"))
    try:
        stats_by_class = eda.get_wisconsin_stats_by_class()
        for cls_name, stats_df in stats_by_class.items():
            with st.expander(f"{cls_name} ({'🟢' if cls_name == 'BENIGN' else '🔴'})"):
                st.dataframe(stats_df, use_container_width=True)
    except Exception as e:
        st.info(f"{get_translation(lang, 'eda.not_available_e')}: {e}")

with tab3:
    st.subheader(get_translation(lang, "eda.correlation_heatmap"))
    st.plotly_chart(eda.plot_correlation_heatmap(), use_container_width=True)

    with st.expander(get_translation(lang, "eda.interpretation")):
        st.markdown("\n".join(get_translation(lang, "eda.interpretation_text")))

with tab4:
    st.subheader(get_translation(lang, "eda.feature_distribution_by_class"))

    n_feat = st.slider(get_translation(lang, "eda.number_of_features"), 5, 30, 10, key="n_feat_box")
    st.plotly_chart(eda.plot_wisconsin_boxplots(n_feat), use_container_width=True)

    st.subheader(get_translation(lang, "eda.histograms_by_class"))
    n_hist = st.slider(get_translation(lang, "eda.number_of_features"), 5, 30, 10, key="n_feat_hist")
    st.plotly_chart(eda.plot_feature_distributions(n_hist), use_container_width=True)

with tab5:
    st.subheader(get_translation(lang, "eda.raw_data_title"))

    dataset_choice = st.selectbox(
        get_translation(lang, "eda.select_dataset"),
        get_translation(lang, "eda.dataset_options"),
    )

    # Map back to the keys we use internally
    if lang == "es":
        source_map = {
            "Calcificaciones": eda.calc_all,
            "Masas": eda.mass_all,
            "Wisconsin": eda.wisconsin_data,
            "Metadatos": eda.meta,
        }
    else:
        source_map = {
            "Calcifications": eda.calc_all,
            "Masses": eda.mass_all,
            "Wisconsin": eda.wisconsin_data,
            "Metadata": eda.meta,
        }

    df_raw = source_map.get(dataset_choice)
    if df_raw is not None:
        st.dataframe(df_raw, use_container_width=True)
        st.caption(f"{get_translation(lang, 'eda.rows')}: {len(df_raw)} | {get_translation(lang, 'eda.columns_short')}: {len(df_raw.columns)}")

        csv_bytes = df_raw.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=get_translation(lang, "eda.download_csv", dataset=dataset_choice),
            data=csv_bytes,
            file_name=f"{dataset_choice.lower()}.csv",
            mime="text/csv",
        )
    else:
        st.info(get_translation(lang, "eda.dataset_not_available"))
