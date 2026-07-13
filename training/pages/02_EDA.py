from pathlib import Path

import streamlit as st

from config import DRIVE_BASE
from modules.eda import BreastCancerEDA


@st.cache_resource
def load_eda(base_path: str) -> BreastCancerEDA:
    eda = BreastCancerEDA(base_path)
    eda.load_all_data()
    return eda


st.title("📋 Análisis Exploratorio de Datos (EDA)")
st.markdown(
    f"**Ruta base:** `{DRIVE_BASE}`  \n"
    "Este módulo realiza el análisis exploratorio completo de los datasets "
    "de cáncer de mama (CBIS-DDSM + Wisconsin)."
)

drive_ok = Path(DRIVE_BASE).exists()
if not drive_ok:
    st.warning(
        f"⚠️ Google Drive no está montado en `{DRIVE_BASE}`. "
        "Verifica que hayas montado Drive y que la ruta sea correcta."
    )
    st.stop()

try:
    eda = load_eda(DRIVE_BASE)
except Exception as e:
    st.error(f"Error cargando datos: {e}")
    st.stop()

summary = eda.get_data_summary()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Calcificaciones", summary["calcificaciones"])
col2.metric("Masas", summary["masas"])
col3.metric("Metadatos", summary["metadatos"])
col4.metric("Wisconsin (tabular)", summary["wisconsin"])

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Resumen",
    "🔄 Distribuciones",
    "📈 Correlaciones",
    "🔬 Características",
    "📄 Datos Crudos",
])

with tab1:
    st.subheader("Resumen de Datasets")

    st.markdown("#### CBIS-DDSM - Calcificaciones")
    if eda.calc_all is not None:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Total casos:** {len(eda.calc_all)}")
            st.markdown(f"**Columnas:** {list(eda.calc_all.columns)}")
        with c2:
            st.dataframe(eda.calc_all.head(5), use_container_width=True)

    st.markdown("#### CBIS-DDSM - Masas")
    if eda.mass_all is not None:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Total casos:** {len(eda.mass_all)}")
            st.markdown(f"**Columnas:** {list(eda.mass_all.columns)}")
        with c2:
            st.dataframe(eda.mass_all.head(5), use_container_width=True)

    st.markdown("#### Wisconsin Breast Cancer")
    if eda.wisconsin_data is not None:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Total casos:** {len(eda.wisconsin_data)}")
            st.markdown(f"**Columnas:** {list(eda.wisconsin_data.columns)}")
        with c2:
            st.dataframe(eda.wisconsin_data.head(5), use_container_width=True)

    mapping = eda.get_image_mapping_stats()
    if mapping["series_en_meta"] > 0:
        st.markdown("#### Correspondencia Imágenes - Metadatos")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Series en meta.csv", mapping["series_en_meta"])
        mc2.metric("Carpetas de imágenes", mapping["carpetas_imagenes"])
        mc3.metric("Coincidencias", mapping["coincidencias"])

    st.subheader("Estadísticos Descriptivos - Wisconsin")
    try:
        st.dataframe(eda.get_wisconsin_descriptive_stats(), use_container_width=True)
    except Exception:
        st.info("No disponible aún.")

with tab2:
    st.subheader("Distribución de Patologías")
    st.plotly_chart(eda.plot_pathology_distribution(), use_container_width=True)

    st.subheader("Distribución BI-RADS Assessment")
    st.plotly_chart(eda.plot_birads_distribution(), use_container_width=True)

    st.subheader("Distribución de Subtlety")
    st.plotly_chart(eda.plot_subtlety_distribution(), use_container_width=True)

    st.subheader("Estadísticas por Clase (Wisconsin)")
    try:
        stats_by_class = eda.get_wisconsin_stats_by_class()
        for cls_name, stats_df in stats_by_class.items():
            with st.expander(f"{cls_name} ({'🟢' if cls_name == 'BENIGN' else '🔴'})"):
                st.dataframe(stats_df, use_container_width=True)
    except Exception as e:
        st.info(f"No disponible: {e}")

with tab3:
    st.subheader("Matriz de Correlación - Wisconsin")
    st.plotly_chart(eda.plot_correlation_heatmap(), use_container_width=True)

    with st.expander("📖 Interpretación"):
        st.markdown(
            """
- **Valores cercanos a +1**: correlación positiva fuerte (ambas variables aumentan juntas)
- **Valores cercanos a -1**: correlación negativa fuerte (una aumenta, la otra disminuye)
- **Valores cercanos a 0**: correlación débil o nula
- Las características de `radius`, `perimeter` y `area` suelen estar altamente correlacionadas
  (son medidas geométricamente relacionadas del mismo núcleo celular)
"""
        )

with tab4:
    st.subheader("Distribución de Características por Clase")

    n_feat = st.slider("Número de características a mostrar", 5, 30, 10, key="n_feat_box")
    st.plotly_chart(eda.plot_wisconsin_boxplots(n_feat), use_container_width=True)

    st.subheader("Histogramas por Clase")
    n_hist = st.slider("Número de características a mostrar", 5, 30, 10, key="n_feat_hist")
    st.plotly_chart(eda.plot_feature_distributions(n_hist), use_container_width=True)

with tab5:
    st.subheader("Datos Crudos")

    dataset_choice = st.selectbox(
        "Seleccionar dataset",
        ["Calcificaciones", "Masas", "Wisconsin", "Metadatos"],
    )

    source_map = {
        "Calcificaciones": eda.calc_all,
        "Masas": eda.mass_all,
        "Wisconsin": eda.wisconsin_data,
        "Metadatos": eda.meta,
    }

    df_raw = source_map.get(dataset_choice)
    if df_raw is not None:
        st.dataframe(df_raw, use_container_width=True)
        st.caption(f"Filas: {len(df_raw)} | Columnas: {len(df_raw.columns)}")

        csv_bytes = df_raw.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"⬇️ Descargar {dataset_choice} como CSV",
            data=csv_bytes,
            file_name=f"{dataset_choice.lower()}.csv",
            mime="text/csv",
        )
    else:
        st.info("Dataset no disponible.")
