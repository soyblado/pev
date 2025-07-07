# mega_buscador_pev_mejorado_gemini.py
# VERSIÓN 2.3 - CORRECCIÓN DE ERROR DE CONEXIÓN (WinError 10061)
# Mejoras: Estructura de análisis robusta para prevenir cierres prematuros del driver.

import streamlit as st
import time
import random
import re
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from deep_translator import GoogleTranslator
from datetime import datetime
import hashlib

# ==========================================
# CONFIGURACIÓN INICIAL
# ==========================================

st.set_page_config(
    page_title="Mega Buscador PEV",
    page_icon="🔥",
    layout="wide"
)

# ==========================================
# PAÍSES ORGANIZADOS POR NIVELES
# ==========================================

NIVELES_PAIS = {
    "Primer Nivel": {
        "countries": ["US", "CA", "GB", "DE", "NL", "FR", "AU", "NZ", "BR"],
        "priority": "MÁXIMA",
        "description": "Monedas fuertes + Brasil (Hotmart HQ)"
    },
    "Segundo Nivel": {
        "countries": ["JP", "KR", "CN", "ZA"],
        "priority": "ALTA",
        "description": "Mercados emergentes con potencial"
    },
    "Tercer Nivel": {
        "countries": ["MX", "ES", "AR", "CO", "CL", "PE", "IN", "ID", "NG", "KE", "EG", "MA"],
        "priority": "MODERADA",
        "description": "Mercados en desarrollo"
    }
}

# ==========================================
# NICHOS DE ALTO RENDIMIENTO
# ==========================================

HIGH_PERFORMING_NICHES = {
    "religious": {
        "performance": "EXCELENTE", "best_countries": ["BR"],
        "note": "Nichos religiosos funcionan muy bien en Brasil.",
        "keywords": ["biblia", "oracion", "fe", "cristiano", "iglesia"]
    },
    "make_money": {
        "performance": "EXCELENTE", "best_countries": ["US", "GB", "CA"],
        "keywords": ["make money", "passive income", "affiliate marketing", "dropshipping"]
    },
    "health_fitness": {
        "performance": "MUY BUENA", "universal": True,
        "keywords": ["weight loss", "fitness", "diet", "health", "workout"]
    },
    "business": {
        "performance": "BUENA", "best_countries": ["US", "GB", "DE"],
        "keywords": ["business", "entrepreneur", "marketing", "sales"]
    }
}

# ==========================================
# CONFIGURACIONES GENERALES
# ==========================================

LANGS = {
    "Español": "spanish", "Portugués": "portuguese", "Inglés": "english",
    "Francés": "french", "Alemán": "german"
}
LANG2ISO = {
    "spanish": "es", "portuguese": "pt", "english": "en",
    "french": "fr", "german": "de"
}

PAISES_SPANISH = ["ES", "MX", "AR", "CO", "CL", "PE"]
PAISES_PORTUGUESE = ["BR"]
PAISES_ENGLISH = ["US", "CA", "GB", "AU", "NZ", "ZA", "NG", "KE"]
PAISES_FRENCH = ["FR", "CA", "MA"]
PAISES_GERMAN = ["DE", "NL"]

COUNTRY2NAME = {
    "US": "Estados Unidos", "CA": "Canadá", "MX": "México", "GB": "Reino Unido",
    "DE": "Alemania", "ES": "España", "NL": "Países Bajos", "FR": "Francia",
    "CN": "China", "IN": "India", "JP": "Japón", "KR": "Corea del Sur",
    "ID": "Indonesia", "BR": "Brasil", "AR": "Argentina", "CO": "Colombia",
    "CL": "Chile", "PE": "Perú", "AU": "Australia", "NZ": "Nueva Zelanda",
    "ZA": "Sudáfrica", "NG": "Nigeria", "KE": "Kenia", "EG": "Egipto", "MA": "Marruecos"
}
ALL_COUNTRIES = list(COUNTRY2NAME.keys())

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
]

# ==========================================
# FUNCIONES DE UTILIDAD
# ==========================================

def get_driver():
    """Inicializa y devuelve un driver de Selenium. Ya no usa cache para asegurar un driver fresco."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"--user-agent={random.choice(UA_LIST)}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    try:
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except WebDriverException as e:
        st.error(f"Error al inicializar el WebDriver: {e}")
        st.error("Asegúrate de que tienes Google Chrome y el ChromeDriver correcto instalados y accesibles.")
        return None

def assess_product_complexity(description):
    text_lower = description.lower()
    simple_indicators = ["ebook", "pdf", "guía", "guide", "manual", "prompts", "plantilla", "template"]
    complex_indicators = ["aplicación", "application", "plataforma", "platform", "software", "app", "sistema", "saas"]
    medium_indicators = ["curso", "course", "video", "training", "masterclass", "webinar"]

    if any(indicator in text_lower for indicator in complex_indicators):
        return {"complexity": "COMPLEJA", "recommendation": "❌ EVITAR", "color": "🔴"}
    elif any(indicator in text_lower for indicator in simple_indicators):
        return {"complexity": "SIMPLE", "recommendation": "✅ MODELAR", "color": "🟢"}
    elif any(indicator in text_lower for indicator in medium_indicators):
        return {"complexity": "MEDIA", "recommendation": "⚠️ CONSIDERAR", "color": "🟡"}
    else:
        return {"complexity": "DESCONOCIDA", "recommendation": "❓ REVISAR", "color": "⚪"}

def validate_viral_offer(total_ads, duplications):
    status, confidence, action, priority = "❌ EVITAR", "BAJA", "BUSCAR OTROS", 5
    if total_ads >= 100:
        status, confidence, action, priority = "🔥 SÚPER VIRAL", "MÁXIMA", "MODELAR INMEDIATAMENTE", 1
    elif total_ads >= 50:
        status, confidence, action, priority = "🚀 MUY VIRAL", "ALTA", "MODELAR HOY", 2
    elif total_ads >= 30:
        status, confidence, action, priority = "✅ VIRAL", "BUENA", "MODELAR EN 24H", 3
    elif total_ads >= 10:
        status, confidence, action, priority = "⚠️ POSIBLE", "MEDIA", "INVESTIGAR MÁS", 4

    duplication_bonus = " + ALTA DUPLICACIÓN" if duplications >= 10 else " + DUPLICACIÓN MEDIA" if duplications >= 5 else ""

    return {
        "status": status + duplication_bonus, "confidence": confidence, "action": action,
        "priority": priority
    }

def obtener_info_nivel_pais(country_code):
    for nivel_nombre, nivel_data in NIVELES_PAIS.items():
        if country_code in nivel_data["countries"]:
            return {
                "nivel": nivel_nombre,
                "priority": nivel_data["priority"],
                "description": nivel_data["description"]
            }
    return {"nivel": "Desconocido", "priority": "BAJA", "description": "No clasificado"}

def traducir_palabras(palabras, idioma_destino):
    if not palabras: return []
    if idioma_destino == "spanish": return palabras

    iso_code = LANG2ISO.get(idioma_destino, "en")
    try:
        return GoogleTranslator(source="auto", target=iso_code).translate_batch(palabras)
    except Exception as e:
        st.warning(f"Error en traducción en lote: {e}. Intentando una por una.")
        traducidas = []
        for palabra in palabras:
            try:
                traducidas.append(GoogleTranslator(source="auto", target=iso_code).translate(palabra))
                time.sleep(0.3)
            except Exception as e_single:
                st.warning(f"No se pudo traducir '{palabra}': {e_single}")
                traducidas.append(palabra)
        return traducidas

def count_ads_quick(driver, keyword, country):
    try:
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={keyword}"
        driver.get(url)
        result_selector = "div[class*='_7jvw']"
        wait = WebDriverWait(driver, 10)
        result_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, result_selector)))
        result_text = result_element.text

        numbers = re.findall(r'[\d,]+', result_text)
        if numbers:
            return int(numbers[0].replace(',', ''))
        return 0
    except (TimeoutException, NoSuchElementException):
        return 0
    except Exception as e:
        # Devuelve el error para que la función principal lo muestre
        raise e

# ==========================================
# FUNCIONES DE PROCESO
# ==========================================

def ejecutar_analisis_demanda(keywords, paises_seleccionados):
    """
    Función centralizada para el análisis de demanda.
    Inicia un driver, realiza todas las búsquedas y luego lo cierra.
    """
    driver = get_driver()
    if not driver:
        st.error("No se pudo iniciar el navegador. El análisis no puede continuar.")
        return []

    resultados = []
    try:
        with st.spinner("Analizando demanda... (Esto puede tardar un poco)"):
            pais_lang_map = {p: "spanish" for p in PAISES_SPANISH}
            pais_lang_map.update({p: "portuguese" for p in PAISES_PORTUGUESE})
            pais_lang_map.update({p: "english" for p in PAISES_ENGLISH})
            pais_lang_map.update({p: "french" for p in PAISES_FRENCH})
            pais_lang_map.update({p: "german" for p in PAISES_GERMAN})
            
            total_searches = len(paises_seleccionados) * len(keywords)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, pais in enumerate(paises_seleccionados):
                nivel_info = obtener_info_nivel_pais(pais)
                idioma_pais = pais_lang_map.get(pais, "english")
                keywords_traducidas = traducir_palabras(keywords, idioma_pais)

                for j, (original_kw, keyword_traducida) in enumerate(zip(keywords, keywords_traducidas)):
                    current_search = i * len(keywords) + j
                    progress_bar.progress((current_search + 1) / total_searches)
                    status_text.text(f"Buscando: '{keyword_traducida}' en {COUNTRY2NAME.get(pais, pais)}...")
                    
                    try:
                        count = count_ads_quick(driver, keyword_traducida, pais)
                        viral_status = validate_viral_offer(count, 0)
                        
                        resultados.append({
                            "País": f"{COUNTRY2NAME[pais]} ({pais})",
                            "Nivel": nivel_info["nivel"],
                            "Prioridad": nivel_info["priority"],
                            "Keyword Original": original_kw,
                            "Keyword Búsqueda": keyword_traducida,
                            "Anuncios": count,
                            "Estado Viral": viral_status["status"],
                            "Acción": viral_status["action"]
                        })
                    except Exception as e:
                        st.error(f"Error contando anuncios para '{keyword_traducida}' en {pais}: {e}")
                        # Añade una fila de error para saber qué falló
                        resultados.append({
                            "País": f"{COUNTRY2NAME[pais]} ({pais})", "Nivel": nivel_info["nivel"], "Prioridad": nivel_info["priority"],
                            "Keyword Original": original_kw, "Keyword Búsqueda": keyword_traducida, "Anuncios": "ERROR",
                            "Estado Viral": "ERROR", "Acción": "Revisar Conexión"
                        })

        status_text.success("¡Análisis completado!")
        return resultados

    finally:
        st.info("Cerrando el navegador...")
        driver.quit()

# ==========================================
# INTERFAZ DE STREAMLIT
# ==========================================

st.title("🔥 Mega Buscador PEV")
st.markdown("### *Metodología de Espionaje Viral de Productos*")

st.sidebar.header("🎯 Herramientas")
menu = st.sidebar.radio(
    "Selecciona una herramienta:",
    [
        "🚀 Guía de Inicio Rápido", "📊 Demanda por País", "🔎 Búsqueda de Anuncios",
        "🔬 Análisis Profundo de URL", "🕵️‍♂️ Análisis de Competidores", "🎯 Nichos de Alto Rendimiento",
        "📋 Checklist del Proceso"
    ]
)

# --- PÁGINA: GUÍA DE INICIO ---
if menu == "🚀 Guía de Inicio Rápido":
    st.header("🚀 Guía de Inicio Rápido - Espionaje Viral")
    st.markdown("""
    ## 🎯 **Proceso de Espionaje Viral**
    ### **Paso 1: Priorización Inteligente por Niveles**
    - 🔥 **Primer Nivel**: US, CA, GB, DE, BR... (máxima prioridad).
    - ⭐ **Segundo Nivel**: JP, KR, CN, ZA... (alta prioridad).
    - 📝 **Tercer Nivel**: MX, ES, CO... (prioridad moderada).
    """)

# --- PÁGINA: DEMANDA POR PAÍS ---
elif menu == "📊 Demanda por País":
    st.header("📊 Análisis de Demanda por País")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🔥 Primer Nivel (Prioridad Máxima)")
        st.info(NIVELES_PAIS["Primer Nivel"]["description"])
    with col2:
        st.markdown("### ⭐ Segundo Nivel (Alta Prioridad)")
        st.info(NIVELES_PAIS["Segundo Nivel"]["description"])
    with col3:
        st.markdown("### 📝 Tercer Nivel (Prioridad Moderada)")
        st.info(NIVELES_PAIS["Tercer Nivel"]["description"])
    st.markdown("---")

    col1, col2 = st.columns([2, 3])
    with col1:
        keywords_input = st.text_area("Palabras clave (una por línea):", "ebook marketing\nfinance course\nexercise guide", height=150)
    with col2:
        st.markdown("**Selección de países por Nivel:**")
        include_nivel1 = st.checkbox("🔥 Incluir Primer Nivel (Recomendado)", value=True)
        include_nivel2 = st.checkbox("⭐ Incluir Segundo Nivel", value=False)
        include_nivel3 = st.checkbox("📝 Incluir Tercer Nivel", value=False)

        paises_para_seleccion = []
        if include_nivel1: paises_para_seleccion.extend(NIVELES_PAIS["Primer Nivel"]["countries"])
        if include_nivel2: paises_para_seleccion.extend(NIVELES_PAIS["Segundo Nivel"]["countries"])
        if include_nivel3: paises_para_seleccion.extend(NIVELES_PAIS["Tercer Nivel"]["countries"])

        paises_selected = st.multiselect(
            "O ajusta la selección manualmente:",
            options=ALL_COUNTRIES, default=paises_para_seleccion,
            format_func=lambda x: f"{COUNTRY2NAME.get(x, x)} ({x})"
        )

    if st.button("🔍 Medir Demanda", type="primary"):
        if keywords_input and paises_selected:
            keywords = [kw.strip() for kw in keywords_input.split("\n") if kw.strip()]
            
            resultados_analisis = ejecutar_analisis_demanda(keywords, paises_selected)

            if resultados_analisis:
                df = pd.DataFrame(resultados_analisis)
                nivel_order = {"Primer Nivel": 1, "Segundo Nivel": 2, "Tercer Nivel": 3, "Desconocido": 4}
                df["Orden"] = df["Nivel"].map(nivel_order)
                df_sorted = df.sort_values(["Orden", "Anuncios"], ascending=[True, False]).drop("Orden", axis=1)
                st.dataframe(df_sorted, use_container_width=True)
                
                # Gráfico de resultados válidos
                df_valid = df[df['Anuncios'] != 'ERROR'].copy()
                df_valid['Anuncios'] = pd.to_numeric(df_valid['Anuncios'])
                df_chart = df_valid[df_valid["Anuncios"] > 0].head(15).iloc[::-1]
                if not df_chart.empty:
                    fig, ax = plt.subplots(figsize=(12, 8))
                    nivel_colors = {"Primer Nivel": "#ff4444", "Segundo Nivel": "#ffaa44", "Tercer Nivel": "#44aaff"}
                    colors = [nivel_colors.get(nivel, "#cccccc") for nivel in df_chart["Nivel"]]
                    ax.barh(range(len(df_chart)), df_chart["Anuncios"], color=colors)
                    ax.set_yticks(range(len(df_chart)))
                    ax.set_yticklabels([f"{row['País']} - {row['Keyword Búsqueda']}" for _, row in df_chart.iterrows()])
                    ax.set_xlabel("Número de Anuncios")
                    ax.set_title("Top 15 Resultados de Demanda (Organizado por Nivel)")
                    st.pyplot(fig)
            else:
                st.warning("No se generaron resultados para esta búsqueda.")
        else:
            st.error("Por favor, ingresa palabras clave y selecciona al menos un país.")

else:
    # Placeholder para otras páginas del menú
    st.info("Selecciona una herramienta del menú de la izquierda para comenzar.")

st.sidebar.markdown("---")
st.sidebar.info("Mega Buscador PEV v2.3")