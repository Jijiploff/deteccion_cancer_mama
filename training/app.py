import streamlit as st

from modules.auth import require_auth, logout, check_auth
from config import APP_TITLE, APP_ICON

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

require_auth()

PAGES = {
    "📊 Dashboard": "pages/01_Dashboard.py",
    "📋 EDA - Análisis Exploratorio": "pages/02_EDA.py",
    "🧠 Entrenamiento": "pages/03_Training.py",
    "🔁 Validación Cruzada": "pages/04_CrossValidation.py",
    "⚙️ Hiperparámetros": "pages/05_HyperparameterTuning.py",
    "📈 Pruebas Estadísticas": "pages/06_StatisticalTests.py",
    "📑 Reportes": "pages/07_Reports.py",
}

st.sidebar.markdown(
    f"# {APP_ICON} {APP_TITLE}",
)
st.sidebar.markdown("---")

if check_auth():
    username = st.session_state.get("username", "admin")
    st.sidebar.markdown(f"**Usuario:** {username}")
    st.sidebar.markdown("---")

    selected = None
    for label in PAGES:
        if st.sidebar.button(label, use_container_width=True, key=f"nav_{label}"):
            selected = label

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        logout()

    page_file = st.session_state.get("current_page", None)

    if selected:
        st.session_state["current_page"] = PAGES[selected]
        st.rerun()

    if page_file and page_file in PAGES.values():
        try:
            exec(open(page_file, encoding="utf-8").read())
        except Exception as e:
            st.error(f"Error al cargar la página: {e}")
    else:
        exec(open("pages/01_Dashboard.py", encoding="utf-8").read())
