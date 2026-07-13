import os
import hashlib
import streamlit as st

USERS = {
    "admin": os.getenv("ADMIN_PASSWORD", "cancer_mama_2024"),
}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate(username: str, password: str) -> bool:
    expected = USERS.get(username)
    if expected and password == expected:
        return True
    return False


def login_form():
    st.markdown("## Inicio de Sesión")
    st.markdown("Ingrese sus credenciales para acceder al panel de entrenamiento.")

    with st.form("login_form"):
        username = st.text_input("Usuario", placeholder="admin", key="login_user")
        password = st.text_input(
            "Contraseña",
            type="password",
            placeholder="••••••••",
            key="login_pass",
        )
        submitted = st.form_submit_button("Ingresar", type="primary", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Debe ingresar usuario y contraseña.")
                return False
            if authenticate(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
                return False
    return False


def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.rerun()


def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    return st.session_state["authenticated"]


def require_auth():
    if not check_auth():
        st.set_page_config(
            page_title="Login - Training Dashboard",
            page_icon="🔐",
            layout="centered",
        )
        st.title("🩺 Sistema de Detección de Cáncer de Mama")
        login_form()
        st.stop()
