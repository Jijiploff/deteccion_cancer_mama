from pathlib import Path

import streamlit as st

from config import DATA_DIR, TABULAR_DIR, RESULTS_DIR
from modules.eda import BreastCancerEDA
from modules.i18n import get_translation


lang = st.session_state.get("language", "es")


@st.cache_resource
def load_eda() -> BreastCancerEDA:
    eda = BreastCancerEDA(
        csv_path=str(DATA_DIR),
        tabular_path=str(TABULAR_DIR),
        results_path=str(RESULTS_DIR),
    )
    eda.load_all_data()
    return eda


st.title(get_translation(lang, "eda.title"))
st.markdown(get_translation(lang, "eda.description"))

# Verificar que los CSVs existen
if not DATA_DIR.exists():
    st.warning(f"Directorio de datos no encontrado: `{DATA_DIR}`")
    st.stop()

try:
    eda = load_eda()
except Exception as e:
    st.error(f"{get_translation(lang, 'eda.error_loading_data')}: {e}")
    st.stop()

summary = eda.get_data_summary()

col1, col2, col3, col4 = st.columns(4)
col1.metric(get_translation(lang, "eda.calcificaciones"), summary["calcificaciones"])
col2.metric(get_translation(lang, "eda.masas"), summary["masas"])
col3.metric(get_translation(lang, "eda.metadatos"), summary["metadatos"])
col4.metric(get_translation(lang, "eda.wisconsin_tabular"), summary["wisconsin"])

# ── Tabs ────────────────────────────────────────────────
tab_summary, tab_dist, tab_corr, tab_features, tab_raw = st.tabs([
    get_translation(lang, "eda.tabs.summary"),
    get_translation(lang, "eda.tabs.distributions"),
    get_translation(lang, "eda.tabs.correlations"),
    get_translation(lang, "eda.tabs.features"),
    get_translation(lang, "eda.tabs.raw_data"),
])

# TAB 1: Summary
with tab_summary:
    st.subheader(get_translation(lang, "eda.dataset_summary"))

    datasets = {
        get_translation(lang, "eda.cbis_ddsm_calc"): eda.calc_all,
        get_translation(lang, "eda.cbis_ddsm_mass"): eda.mass_all,
        get_translation(lang, "eda.wisconsin_breast_cancer"): eda.wisconsin_data,
    }

    for name, df in datasets.items():
        if df is not None and len(df) > 0:
            st.markdown(f"**{name}**")
            c1, c2 = st.columns(2)
            c1.metric(get_translation(lang, "eda.total_cases"), len(df))
            c2.metric(get_translation(lang, "eda.columns"), len(df.columns))

    if eda.meta is not None:
        st.subheader(get_translation(lang, "eda.image_mapping"))
        mapping = eda.get_image_mapping_stats()
        cc1, cc2, cc3 = st.columns(3)
        cc1.metric(get_translation(lang, "eda.series_in_meta"), mapping["series_en_meta"])
        cc2.metric(get_translation(lang, "eda.image_folders"), mapping["carpetas_imagenes"])
        cc3.metric(get_translation(lang, "eda.matches"), mapping["coincidencias"])

    if eda.wisconsin_data is not None:
        st.subheader(get_translation(lang, "eda.descriptive_stats"))
        stats = eda.get_wisconsin_descriptive_stats()
        st.dataframe(stats, use_container_width=True)

# TAB 2: Distributions
with tab_dist:
    if eda.is_loaded:
        st.subheader(get_translation(lang, "eda.pathology_distribution"))
        st.plotly_chart(eda.plot_pathology_distribution(), use_container_width=True)

        st.subheader(get_translation(lang, "eda.birads_distribution"))
        st.plotly_chart(eda.plot_birads_distribution(), use_container_width=True)

        st.subheader(get_translation(lang, "eda.subtlety_distribution"))
        st.plotly_chart(eda.plot_subtlety_distribution(), use_container_width=True)

        st.subheader(get_translation(lang, "eda.stats_by_class"))
        stats_by_class = eda.get_wisconsin_stats_by_class()
        for cls_name, cls_stats in stats_by_class.items():
            st.markdown(f"**{cls_name}**")
            st.dataframe(cls_stats, use_container_width=True)
    else:
        st.info(get_translation(lang, "eda.not_available_e"))

# TAB 3: Correlations
with tab_corr:
    if eda.is_loaded:
        st.subheader(get_translation(lang, "eda.correlation_heatmap"))
        st.plotly_chart(eda.plot_correlation_heatmap(), use_container_width=True)

        with st.expander(get_translation(lang, "eda.interpretation")):
            for line in get_translation(lang, "eda.interpretation_text"):
                st.markdown(line)
    else:
        st.info(get_translation(lang, "eda.not_available_e"))

# TAB 4: Features
with tab_features:
    if eda.is_loaded:
        st.subheader(get_translation(lang, "eda.feature_distribution_by_class"))
        n_features = st.slider(
            get_translation(lang, "eda.number_of_features"),
            min_value=5, max_value=30, value=10, step=5,
        )

        st.markdown("**Boxplots**")
        st.plotly_chart(eda.plot_wisconsin_boxplots(n_features=n_features), use_container_width=True)

        st.markdown(f"**{get_translation(lang, 'eda.histograms_by_class')}**")
        st.plotly_chart(eda.plot_feature_distributions(n_features=n_features), use_container_width=True)
    else:
        st.info(get_translation(lang, "eda.not_available_e"))

# TAB 5: Raw Data
with tab_raw:
    options = get_translation(lang, "eda.dataset_options")
    selected = st.selectbox(get_translation(lang, "eda.select_dataset"), options)

    source_map = {
        options[0]: eda.calc_all,
        options[1]: eda.mass_all,
        options[2]: eda.wisconsin_data,
        options[3]: eda.meta,
    }

    df_selected = source_map.get(selected)
    if df_selected is not None and len(df_selected) > 0:
        st.write(f"{get_translation(lang, 'eda.rows')}: {len(df_selected)} | {get_translation(lang, 'eda.columns_short')}: {len(df_selected.columns)}")
        st.dataframe(df_selected, use_container_width=True)

        csv_data = df_selected.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=get_translation(lang, "eda.download_csv", dataset=selected),
            data=csv_data,
            file_name=f"{selected.lower()}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.info(get_translation(lang, "eda.dataset_not_available"))
