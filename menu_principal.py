# menu_principal.py
# Este es el script principal que ejecutarás.
# Actuará como la página de bienvenida de tu aplicación.

import streamlit as st

st.set_page_config(
    page_title="Menú Principal - Mega Buscadores",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Menú Principal de Herramientas")
st.markdown("---")
st.header("Bienvenido a tu centro de control de buscadores.")
st.subheader("Por favor, selecciona una herramienta del menú de la izquierda para comenzar.")

st.info(
    """
    **Instrucciones:**
    1.  En la barra lateral izquierda, verás una lista de todas tus aplicaciones.
    2.  Haz clic en el nombre de la herramienta que deseas utilizar.
    3.  La aplicación seleccionada se cargará en esta ventana.
    """,
    icon="ℹ️"
)