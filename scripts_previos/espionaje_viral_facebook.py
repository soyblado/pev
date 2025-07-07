import streamlit as st
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By

def espionaje_viral_facebook(phrases, country, incognito):
    """
    Realiza espionaje viral en Facebook Ads Library usando frases clave.

    Args:
        phrases (list[str]): Lista de frases clave.
        country (str): Código de país (CO, ES, MX, US, UK, BR, FR).
        incognito (bool): Si usar modo incógnito en el navegador.

    Returns:
        list[dict]: Cada dict contiene 'frase', 'total_ads' y 'ejemplos'.
    """
    # Configuración de Chrome
    opts = ChromeOptions()
    if incognito:
        opts.add_argument("--incognito")
    driver = Chrome(options=opts)
    resultados = []

    for phrase in phrases:
        # Construir URL de búsqueda
        url = (
            "https://www.facebook.com/ads/library/?active_status=all"
            f"&ad_type=all&country={country}&q={phrase}"
        )
        driver.get(url)
        st.write(f"Buscando “{phrase}” en {country}…")

        # Esperar y extraer número de anuncios activos
        driver.implicitly_wait(5)
        try:
            count_elem = driver.find_element(By.CSS_SELECTOR, "div[role='heading']")
            total_ads = int(count_elem.text.split()[0].replace(',', ''))
        except Exception:
            total_ads = 0

        # Capturar hasta 5 ejemplos de anuncios
        ejemplos = []
        try:
            ad_cards = driver.find_elements(By.CSS_SELECTOR, ".x1lliihq")[:5]
            ejemplos = [card.text for card in ad_cards]
        except Exception:
            pass

        resultados.append({
            "frase": phrase,
            "total_ads": total_ads,
            "ejemplos": ejemplos
        })

    driver.quit()
    return resultados


def main():
    st.set_page_config(page_title="Panel de Espionaje Viral", layout="wide")
    menu = st.sidebar.radio(
        "Selecciona una sección",
        [
            "🚀 Guía de Inicio Rápido",
            "🔍 Espionaje Viral",
            "🔎 Búsqueda General por Palabras Clave",
            "🔬 Análisis Profundo de Página de Resultados",
            "🕵️ Análisis Específico de Competidores",
            "🧮 Calculadora de Rentabilidad",
            "📜 Checklist del Proceso"
        ]
    )

    if menu == "🚀 Guía de Inicio Rápido":
        st.title("Guía de Inicio Rápido")
        st.markdown(
            """
            1. Selecciona 'Espionaje Viral'
            2. Ingresa frases clave separadas por comas
            3. Elige país e inicia
            4. Analiza resultados
            5. Itera con nuevas frases
            """
        )

    elif menu == "🔍 Espionaje Viral":
        st.title("🔍 Espionaje Viral")
        raw = st.text_area("Frases clave (separadas por comas)")
        country = st.selectbox("País", ["CO","ES","MX","US","UK","BR","FR"])
        inc = st.checkbox("Abrir en incógnito", value=True)
        if st.button("Iniciar Espionaje Viral"):
            phrases = [p.strip() for p in raw.split(",") if p.strip()]
            if phrases:
                with st.spinner("Ejecutando espionaje…"):
                    data = espionaje_viral_facebook(phrases, country, inc)
                for item in data:
                    st.metric(
                        label=f"“{item['frase']}” → Anuncios activos",
                        value=item['total_ads']
                    )
                    st.write("Ejemplos de anuncios:", item['ejemplos'])
            else:
                st.warning("Por favor ingresa al menos una frase clave.")

    else:
        st.warning("Funcionalidad pendiente para esta sección.")

if __name__ == "__main__":
    main()
