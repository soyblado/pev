# dashboard_app.py
# VERSIÓN CON ENTRADA MANUAL POR COMAS - 19/JUN/2025
# MEJORA: Eliminada la dependencia de 'googletrans'. Sistema más robusto y fiable.

import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
import time
import re
import base64

# --- CONFIGURACIÓN GENERAL DE LA APP ---
st.set_page_config(
    page_title="Investigador de E-books",
    page_icon="📚",
    layout="wide"
)

# --- INICIALIZAR SESSION STATE ---
if 'organized_keywords' not in st.session_state:
    st.session_state.organized_keywords = None

# --- PARÁMETROS GLOBALES ---
BASE_URL = 'https://www.facebook.com/ads/library/'
TARGET_COUNTRIES_WITH_LANG = {
    'CO': ('Colombia', 'es'),
    'ES': ('España', 'es'),
    'MX': ('México', 'es'),
    'US': ('Estados Unidos', 'en'),
    'GB': ('Reino Unido', 'en'),
    'BR': ('Brasil', 'pt'),
    'FR': ('Francia', 'fr')
}

RESULTS_TEXT_XPATH = '//div[contains(text(), " resultado") or contains(text(), " result")]'
AD_CARD_SELECTOR_XPATH = "//div[contains(@class, 'x1yztbdb') and contains(@class, 'x1n2onr6') and contains(@class, 'xh8yej3') and contains(@class, 'x1ja2u2z')]"

# --- FUNCIONES DE LÓGICA (sin cambios) ---
@st.cache_resource
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return webdriver.Chrome(options=options)

def search_by_url(driver, search_url):
    driver.get(search_url)
    try:
        results_text_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, RESULTS_TEXT_XPATH))
        )
        if results_text_element and results_text_element.text:
            results_text = results_text_element.text
            found_numbers = re.findall(r'[\d,.]+', results_text)
            if found_numbers:
                return int(re.sub(r'[,.]', '', found_numbers[0]))
        return 0
    except Exception:
        return 0

def analyze_page_for_copies(driver, page_url, min_copies):
    st.info(f"Navegando a la página de resultados: {page_url}")
    driver.get(page_url)
    winners = []
    try:
        st.write("Esperando a que carguen los anuncios en la página...")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, AD_CARD_SELECTOR_XPATH)))
        time.sleep(5)
        ad_cards = driver.find_elements(By.XPATH, AD_CARD_SELECTOR_XPATH)
        st.write(f"Se encontraron {len(ad_cards)} anuncios en la página para analizar.")

        for card in ad_cards:
            ad_text = card.text
            match = re.search(r"(\d+)\s+anuncios usan esta creatividad", ad_text)
            
            if match:
                num_copies = int(match.group(1))
                if num_copies >= min_copies:
                    ad_creative_url = "No encontrada"
                    try:
                        img_element = card.find_element(By.TAG_NAME, "img")
                        ad_creative_url = img_element.get_attribute('src')
                    except Exception: pass
                    
                    landing_page_url = "No encontrado"
                    try:
                        link_elements = card.find_elements(By.TAG_NAME, "a")
                        for link in link_elements:
                            href = link.get_attribute('href')
                            if href and 'facebook.com' not in href and 'fb.me' not in href:
                                landing_page_url = href
                                break
                    except Exception: pass
                    
                    headline = "No encontrado"
                    try:
                        headline_element = card.find_element(By.XPATH, ".//div[@role='heading']")
                        headline = headline_element.text
                    except Exception: pass
                    
                    cta_text = "No encontrado"
                    try:
                        cta_element = card.find_element(By.XPATH, ".//a[@role='button']")
                        cta_text = cta_element.text
                    except Exception: pass

                    winners.append({
                        "text": ad_text, "copies": num_copies,
                        "ad_creative_url": ad_creative_url, "landing_page_url": landing_page_url,
                        "headline": headline, "cta_text": cta_text
                    })
        return winners
    except Exception as e:
        st.error(f"Ocurrió un error al analizar la página. Error: {e}")
        return []

def create_checklist_html():
    html_content = """...""" # Contenido idéntico, omitido
    b64_html = base64.b64encode(html_content.encode()).decode()
    return f"data:text/html;base64,{b64_html}"

# --- INTERFAZ DE LA APLICACIÓN WEB ---
st.title("📚 Panel de Control - Investigador de E-books")

st.sidebar.title("Herramientas de Espionaje")
app_mode = st.sidebar.radio(
    "Selecciona una tarea:",
    ("🚀 Guía de Inicio Rápido",
     "🔎 Búsqueda General por Palabras Clave",
     "🔬 Análisis Profundo de Página de Resultados",
     "🕵️ Análisis Específico de Competidores",
     "🧮 Calculadora de Rentabilidad",
     "📜 Checklist del Proceso")
)

if app_mode == "🚀 Guía de Inicio Rápido":
    st.header("🏁 Guía de Inicio Rápido: Tu Flujo de Trabajo Correcto")
    # ... (Contenido idéntico)

# ======================================================================================
# PÁGINA: BÚSQUEDA GENERAL (NUEVO SISTEMA POR COMAS)
# ======================================================================================
elif app_mode == "🔎 Búsqueda General por Palabras Clave":
    st.header("🔎 Búsqueda General de E-books Ganadores")
    st.info("Introduce tus grupos de palabras clave (uno por línea) y el sistema las organizará para la búsqueda multi-idioma.")

    # --- PASO 1: ENTRADA DE PALABRAS CLAVE POR GRUPO ---
    st.subheader("Paso 1: Prepara tus Palabras Clave")
    manual_keywords_input = st.text_area(
        "Grupos de Palabras Clave (un grupo por línea):",
        height=150,
        placeholder="español,inglés,portugués,francés\nej: libro de cocina,cookbook,livro de receitas,livre de cuisine",
        help="Escribe en cada línea la palabra clave en los 4 idiomas, separadas por comas."
    )

    if st.button("📝 Organizar Palabras Clave"):
        if manual_keywords_input.strip():
            es_list, en_list, pt_list, fr_list = [], [], [], []
            lines = manual_keywords_input.strip().split('\n')
            valid_lines = 0
            for i, line in enumerate(lines):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) == 4:
                    es_list.append(parts[0])
                    en_list.append(parts[1])
                    pt_list.append(parts[2])
                    fr_list.append(parts[3])
                    valid_lines += 1
                else:
                    st.warning(f"La línea #{i+1} no tiene el formato correcto (4 palabras separadas por comas) y será ignorada.")
            
            if valid_lines > 0:
                st.session_state.organized_keywords = {
                    'es': es_list, 'en': en_list, 'pt': pt_list, 'fr': fr_list
                }
                st.success(f"¡Se organizaron {valid_lines} grupos de palabras clave correctamente!")
            else:
                st.error("Ninguna línea tuvo el formato correcto. Asegúrate de seguir el ejemplo: palabra1,palabra2,palabra3,palabra4")
        else:
            st.warning("Por favor, introduce al menos un grupo de palabras clave.")

    # --- PASO 2: REVISAR Y LANZAR BÚSQUEDA ---
    if st.session_state.organized_keywords:
        st.subheader("Paso 2: Revisa y Lanza la Búsqueda")
        
        keywords = st.session_state.organized_keywords
        col1, col2 = st.columns(2)
        with col1:
            st.text_area("Español (ES, CO, MX)", value="\n".join(keywords['es']), disabled=True, key="es_box")
            st.text_area("Portugués (BR)", value="\n".join(keywords['pt']), disabled=True, key="pt_box")
        with col2:
            st.text_area("Inglés (US, GB)", value="\n".join(keywords['en']), disabled=True, key="en_box")
            st.text_area("Francés (FR)", value="\n".join(keywords['fr']), disabled=True, key="fr_box")

        min_ads_input = st.number_input("Mínimo de anuncios para ser 'ganador':", min_value=1, value=15)

        if st.button("🚀 Iniciar Búsqueda Inteligente en todos los países"):
            driver = get_driver()
            st.info("Driver iniciado. ¡Comenzando la búsqueda inteligente!")
            results_container = st.container()
            
            for country_code, (country_name, lang_code) in TARGET_COUNTRIES_WITH_LANG.items():
                keywords_for_this_country = keywords.get(lang_code, [])
                if not keywords_for_this_country:
                    continue
                
                st.write(f"--- Analizando **{country_name.upper()}** con palabras clave en **{lang_code.upper()}** ---")
                for keyword in keywords_for_this_country:
                    if not keyword: continue # Omitir si la palabra clave está vacía
                    st.write(f"Buscando '{keyword}'...")
                    encoded_keyword = quote(keyword)
                    search_url = f"{BASE_URL}?active_status=all&ad_type=all&country={country_code}&q={encoded_keyword}&search_type=keyword_exact_phrase"
                    num_ads = search_by_url(driver, search_url)
                    if num_ads >= min_ads_input:
                        with results_container.expander(f"¡ÉXITO en {country_name.upper()}! - Keyword: '{keyword}' ({num_ads} anuncios)"):
                            st.success(f"Encontrado: '{keyword}' con {num_ads} anuncios.")
                            st.markdown(f"**[Haz clic aquí para ver los anuncios]({search_url})**")
                    time.sleep(1)
            
            st.balloons()
            st.header("¡Búsqueda finalizada!")
            driver.quit()

# --- OTRAS PÁGINAS (SIN CAMBIOS) ---
elif app_mode == "🔬 Análisis Profundo de Página de Resultados":
    st.header("🔬 Análisis Profundo de Página de Resultados")
    # ... (Contenido idéntico)

elif app_mode == "🕵️ Análisis Específico de Competidores":
    st.header("🕵️ Análisis Específico de Competidores")
    # ... (Contenido idéntico)

elif app_mode == "🧮 Calculadora de Rentabilidad":
    st.header("🧮 Calculadora de Rentabilidad y Estrategia")
    # ... (Contenido idéntico)

elif app_mode == "📜 Checklist del Proceso":
    st.header("✅ Checklist: Proceso de Investigación de Principio a Fin")
    # ... (Contenido idéntico)