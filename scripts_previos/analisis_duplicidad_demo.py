import streamlit as st
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import Counter

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

def analizar_duplicidad_creativos(keyword, country, max_anuncios=30):
    driver = get_driver()
    copys = []
    try:
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered&media_type=all"
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.x1lliihq')))
        except Exception:
            pass
        time.sleep(3)
        cards = driver.find_elements(By.CSS_SELECTOR, 'div.x1lliihq')
        if len(cards) == 0:
            cards = driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')
        for card in cards[:max_anuncios]:
            try:
                copy = card.text.strip()
                if len(copy) > 30:
                    copys.append(copy)
            except Exception:
                continue
    finally:
        driver.quit()
    return Counter(copys)

st.title("🔁 Análisis de Duplicidad de Creativos (DEMO)")
st.markdown("Este módulo permite analizar cuántas veces se repite el mismo creativo (copy) en anuncios de Facebook Ads Library.")

keyword = st.text_input("Ingresa una palabra clave para buscar anuncios:")
country = st.text_input("País (código ISO, ej: BR, US, ES):", value="BR")

if st.button("Analizar duplicidad de creativos"):
    with st.spinner("Buscando anuncios y analizando duplicidad..."):
        duplicados = analizar_duplicidad_creativos(keyword, country)
        if duplicados:
            st.success(f"Se analizaron {sum(duplicados.values())} anuncios. Creativos más repetidos:")
            for copy, count in duplicados.most_common(10):
                if count > 1:
                    st.markdown(f"<span style='color:orange'><b>{count}x</b></span> <span style='color:green'>{copy[:120]}...</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<b>1x</b> {copy[:120]}...", unsafe_allow_html=True)
        else:
            st.warning("No se encontraron anuncios o creativos duplicados para esa keyword y país.") 