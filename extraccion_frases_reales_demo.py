import streamlit as st
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-images")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return webdriver.Chrome(options=options)

def extraer_frases_reales_de_anuncios(keyword, country, max_anuncios=20):
    """Busca anuncios reales en Facebook Ads Library y extrae frases del copy de los anuncios encontrados."""
    driver = get_driver()
    frases_extraidas = set()
    try:
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered&media_type=all"
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.x1lliihq')))
        except Exception:
            print("[LOG] No se encontró el selector 'div.x1lliihq' (puede haber cambiado)")
        time.sleep(3)
        cards = driver.find_elements(By.CSS_SELECTOR, 'div.x1lliihq')
        print(f"[LOG] Encontrados {len(cards)} elementos con selector 'div.x1lliihq'")
        # Probar selector alternativo si no encuentra nada
        if len(cards) == 0:
            cards = driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')
            print(f"[LOG] Encontrados {len(cards)} elementos con selector alternativo 'div[role=article]'")
        for card in cards[:max_anuncios]:
            try:
                copy = card.text
                print(f"[LOG] Texto extraído: {copy[:100]}...")
                frases = re.findall(r'([\w\s,\.\-\!\?\:;]{20,200})', copy)
                for frase in frases:
                    frase_limpia = frase.strip().replace('\n', ' ')
                    if 5 <= len(frase_limpia.split()) <= 20:
                        frases_extraidas.add(frase_limpia)
            except Exception as e:
                print(f"[LOG] Error extrayendo frase: {e}")
                continue
    finally:
        driver.quit()
    print(f"[LOG] Total frases extraídas: {len(frases_extraidas)}")
    return list(frases_extraidas)

st.title("📝 Extracción de Frases Reales de Anuncios (DEMO)")
st.markdown("Este módulo permite extraer frases reales de anuncios en Facebook Ads Library para usarlas en búsquedas de productos.")

keyword_frase = st.text_input("Ingresa una palabra clave para extraer frases reales de anuncios:")
country = st.text_input("País (código ISO, ej: BR, US, ES):", value="BR")

if st.button("Buscar frases reales de anuncios"):
    with st.spinner("Buscando anuncios y extrayendo frases reales..."):
        frases_encontradas = extraer_frases_reales_de_anuncios(keyword_frase, country)
        if frases_encontradas:
            st.session_state['frases_extraidas'] = frases_encontradas
            st.success(f"{len(frases_encontradas)} frases extraídas. Selecciona las que quieras usar:")
        else:
            st.warning("No se encontraron frases reales para esa keyword y país.")

if 'frases_extraidas' in st.session_state and st.session_state['frases_extraidas']:
    frases_seleccionadas = st.multiselect("Selecciona frases para usar en la búsqueda de productos:", st.session_state['frases_extraidas'])
    if st.button("Guardar frases seleccionadas para búsqueda"):
        st.session_state['frases_seleccionadas_busqueda'] = frases_seleccionadas
        st.success("Frases guardadas. Ahora puedes usarlas en la búsqueda de productos.") 