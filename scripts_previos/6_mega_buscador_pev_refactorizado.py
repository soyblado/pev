# mega_buscador_pev_refactorizado.py
# VERSIÓN REFACTORIZADA CON MEJORAS DE RENDIMIENTO, CACHING Y ESTRUCTURA
# Mejoras: Gestión de Driver en Sesión + Caching + Persistencia de Resultados + Componentes Nativos

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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from deep_translator import GoogleTranslator
from datetime import datetime, timedelta
import json

# ==========================================
# CONFIGURACIÓN INICIAL Y CARGA DE REGLAS
# ==========================================

st.set_page_config(
    page_title="Mega Buscador PEV (Refactorizado)",
    page_icon="🚀",
    layout="wide"
)

# NOTA: En una aplicación ideal, estos diccionarios estarían en un archivo config.json
# Por simplicidad para este script, se mantienen aquí.
CRISTIAN_KEY_PHRASES = {
    "spanish": ["acceso inmediato a", "descargar ahora gratis", "método comprobado", "transforma tu vida", "descubre el secreto", "guía completa", "sistema probado", "resultados garantizados"],
    "portuguese": ["tenha acesso imediato a", "baixar agora gratis", "metodo comprovado", "transforme sua vida", "descubra o segredo", "guia completo", "sistema comprovado", "resultados garantidos"],
    "english": ["get instant access to", "download now free", "proven method", "transform your life", "discover the secret", "complete guide", "proven system", "guaranteed results"],
    "french": ["accès immédiat à", "télécharger maintenant gratuitement", "méthode prouvée", "transformez votre vie", "découvrez le secret", "guide complet"],
    "german": ["sofortiger zugang zu", "jetzt kostenlos herunterladen", "bewährte methode", "verwandeln sie ihr leben", "entdecken sie das geheimnis"]
}
COUNTRY_TIERS = {
    "tier_1": {"countries": ["US", "CA", "GB", "DE", "NL", "FR", "AU", "NZ", "BR"], "priority": "MÁXIMA", "scraping_intensity": "PROFUNDO", "expected_performance": "EXCELENTE", "description": "Monedas fuertes + Brasil (Hotmart HQ)"},
    "tier_2": {"countries": ["JP", "KR", "CN", "ZA"], "priority": "ALTA", "scraping_intensity": "MEDIO", "expected_performance": "BUENA", "description": "Mercados emergentes con potencial"},
    "tier_3": {"countries": ["MX", "ES", "AR", "CO", "CL", "PE", "IN", "ID", "NG", "KE", "EG", "MA"], "priority": "MODERADA", "scraping_intensity": "LIGERO", "expected_performance": "VARIABLE", "description": "Mercados en desarrollo"}
}
HIGH_PERFORMING_NICHES = {
    "religious": {"performance": "EXCELENTE", "best_countries": ["BR"], "cristian_note": "Los que mejor performan en Brasil", "keywords": ["biblia", "oracion", "fe", "cristiano", "iglesia"]},
    "make_money": {"performance": "EXCELENTE", "best_countries": ["US", "GB", "CA"], "keywords": ["make money", "passive income", "affiliate marketing", "dropshipping"]},
    "health_fitness": {"performance": "MUY BUENA", "universal": True, "keywords": ["weight loss", "fitness", "diet", "health", "workout"]},
    "business": {"performance": "BUENA", "best_countries": ["US", "GB", "DE"], "keywords": ["business", "entrepreneur", "marketing", "sales"]}
}
LANGS = {"Español": "spanish", "Portugués": "portuguese", "Inglés": "english", "Francés": "french", "Alemán": "german"}
LANG2ISO = {"spanish": "es", "portuguese": "pt", "english": "en", "french": "fr", "german": "de"}
PAISES_SPANISH = ["ES", "MX", "AR", "CO", "CL", "PE"]
PAISES_PORTUGUESE = ["BR"]
PAISES_ENGLISH = ["US", "CA", "GB", "AU", "NZ", "ZA", "NG", "KE"]
PAISES_FRENCH = ["FR", "CA", "MA"]
PAISES_GERMAN = ["DE", "NL"]
COUNTRY2NAME = {
    "US": "Estados Unidos", "CA": "Canadá", "MX": "México", "GB": "Reino Unido", "DE": "Alemania", "ES": "España",
    "NL": "Países Bajos", "FR": "Francia", "CN": "China", "IN": "India", "JP": "Japón", "KR": "Corea del Sur",
    "ID": "Indonesia", "BR": "Brasil", "AR": "Argentina", "CO": "Colombia", "CL": "Chile", "PE": "Perú",
    "AU": "Australia", "NZ": "Nueva Zelanda", "ZA": "Sudáfrica", "NG": "Nigeria", "KE": "Kenia", "EG": "Egipto", "MA": "Marruecos"
}
ALL_COUNTRIES = list(COUNTRY2NAME.keys())
UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# ==========================================
# MEJORA: GESTIÓN DE DRIVER DE SELENIUM
# ==========================================

def get_session_driver(incognito=False):
    """Obtiene el driver desde st.session_state o lo crea si no existe."""
    if 'driver' not in st.session_state or st.session_state.driver is None:
        st.write("🔧 Inicializando nuevo driver de Selenium...")
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--user-agent={random.choice(UA_LIST)}")
        if incognito:
            options.add_argument("--incognito")
        try:
            driver = webdriver.Chrome(options=options)
            st.session_state.driver = driver
        except Exception as e:
            st.error(f"❌ No se pudo inicializar el driver de Chrome. Asegúrate de que esté instalado y accesible en tu PATH. Error: {e}")
            st.session_state.driver = None
            return None
    return st.session_state.driver

def quit_session_driver():
    """Cierra el driver y lo elimina del session_state."""
    if 'driver' in st.session_state and st.session_state.driver:
        st.session_state.driver.quit()
        st.session_state.driver = None
        st.info("✅ Driver de Selenium cerrado.")

# ==========================================
# FUNCIONES DE UTILIDAD (CON CACHING)
# ==========================================

def assess_product_complexity(description):
    text_lower = description.lower()
    simple_indicators = ["ebook", "pdf", "guía", "guide", "manual", "prompts", "plantilla", "template"]
    complex_indicators = ["aplicación", "application", "plataforma", "platform", "software", "app", "sistema complejo", "saas"]
    medium_indicators = ["curso", "course", "video", "training", "masterclass", "webinar"]
    
    if any(indicator in text_lower for indicator in complex_indicators):
        return {"complexity": "COMPLEJA", "recommendation": "❌ EVITAR - Bandera roja", "reason": "Muy difícil de modelar", "color": "🔴"}
    elif any(indicator in text_lower for indicator in simple_indicators):
        return {"complexity": "SIMPLE", "recommendation": "✅ MODELAR - Fácil de replicar", "reason": "Ideal para espionaje viral", "color": "🟢"}
    elif any(indicator in text_lower for indicator in medium_indicators):
        return {"complexity": "MEDIA", "recommendation": "⚠️ CONSIDERAR - Revisar", "reason": "Evaluar caso por caso", "color": "🟡"}
    else:
        return {"complexity": "DESCONOCIDA", "recommendation": "❓ REVISAR MANUALMENTE", "reason": "Necesita análisis manual", "color": "⚪"}

def validate_viral_offer(total_ads, duplications):
    if total_ads >= 100: status, confidence, action, priority = "🔥 SÚPER VIRAL", "MÁXIMA", "MODELAR INMEDIATAMENTE", 1
    elif total_ads >= 50: status, confidence, action, priority = "🚀 MUY VIRAL", "ALTA", "MODELAR HOY", 2
    elif total_ads >= 30: status, confidence, action, priority = "✅ VIRAL", "BUENA", "MODELAR EN 24H", 3
    elif total_ads >= 10: status, confidence, action, priority = "⚠️ POSIBLE", "MEDIA", "INVESTIGAR MÁS", 4
    else: status, confidence, action, priority = "❌ EVITAR", "BAJA", "BUSCAR OTROS", 5
    
    duplication_bonus = " + ALTA DUPLICACIÓN" if duplications >= 10 else " + DUPLICACIÓN MEDIA" if duplications >= 5 else ""
    
    return {"status": status + duplication_bonus, "confidence": confidence, "action": action, "priority": priority, "cristian_approved": total_ads >= 30 and duplications >= 5}

def speed_alert_system(product_found_time=None):
    if product_found_time is None: product_found_time = datetime.now()
    hours_passed = (datetime.now() - product_found_time).total_seconds() / 3600
    if hours_passed > 24: return {"status": "🚨 CRÍTICO", "message": f"Han pasado {hours_passed:.1f}h - Oferta puede estar quemada", "action": "VERIFICAR SI AÚN FUNCIONA", "color": "red"}
    elif hours_passed > 12: return {"status": "⚠️ URGENTE", "message": f"Quedan {24-hours_passed:.1f}h - Acelerar modelado", "action": "MODELAR HOY", "color": "orange"}
    else: return {"status": "✅ TIEMPO", "message": f"Tiempo restante: {24-hours_passed:.1f}h", "action": "PROCEDER SEGÚN PLAN", "color": "green"}

def get_country_tier_info(country_code):
    for tier_name, tier_data in COUNTRY_TIERS.items():
        if country_code in tier_data["countries"]:
            return {"tier": tier_name, "priority": tier_data["priority"], "performance": tier_data["expected_performance"], "description": tier_data["description"]}
    return {"tier": "unknown", "priority": "BAJA", "performance": "DESCONOCIDA"}

@st.cache_data # MEJORA: Cache para evitar traducciones repetitivas
def traducir_palabras(palabras, idioma_destino):
    if idioma_destino == "spanish": return palabras
    iso_code = LANG2ISO.get(idioma_destino, "en")
    try:
        translator = GoogleTranslator(source="es", target=iso_code)
        traducidas = translator.translate_batch(list(palabras))
        return traducidas if traducidas else palabras
    except Exception as e:
        st.warning(f"Error traduciendo a {idioma_destino}: {e}. Usando palabras originales.")
        return palabras

# ==========================================
# LÓGICA DE SCRAPING REFACTORIZADA Y CON CACHING
# ==========================================

@st.cache_data(ttl=3600) # Cachear por 1 hora
def _count_ads_logic(keyword, country):
    """Función interna con la lógica de scraping, para ser cacheada."""
    driver = get_session_driver()
    if not driver: return 0
    
    try:
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered&media_type=all"
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        result_element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), ' result') or contains(text(), ' resultado')]")))
        numbers = re.findall(r'\d{1,3}(?:,\d{3})*|\d+', result_element.text)
        return int(numbers[0].replace(',', '').replace('.', '')) if numbers else 0
    except TimeoutException:
        return 0 # No results found or page didn't load
    except Exception as e:
        st.error(f"Error en _count_ads_logic para '{keyword}' en {country}: {e}")
        return 0

def count_ads_quick(keyword, country):
    """Función pública que usa la lógica cacheada."""
    return _count_ads_logic(keyword, country)

@st.cache_data(ttl=3600)
def _obtener_anuncios_logic(keyword, country, max_cards):
    """Función interna de scraping de anuncios para ser cacheada."""
    driver = get_session_driver()
    if not driver: return []
    
    anuncios = []
    try:
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered&media_type=all"
        driver.get(url)
        time.sleep(3)
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
        cards = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='ad-library-card']")
        
        for card in cards[:max_cards]:
            try:
                copy_text = card.find_element(By.CSS_SELECTOR, "div[data-testid='ad-library-card-copy-text']").text
                link = card.find_element(By.CSS_SELECTOR, "a[data-testid='ad-library-card-cta-button']").get_attribute("href")
                complexity = assess_product_complexity(copy_text)
                anuncios.append({
                    "Copy": copy_text[:300] + "..." if len(copy_text) > 300 else copy_text,
                    "Link": link,
                    "Complejidad": complexity["complexity"],
                    "Recomendación": complexity["recommendation"],
                    "Color": complexity["color"]
                })
            except (NoSuchElementException, TimeoutException):
                continue
    except Exception as e:
        st.error(f"Error en _obtener_anuncios_logic para '{keyword}' en {country}: {e}")
    return anuncios

def obtener_anuncios(keyword, country, max_cards=15):
    """Función pública que usa la lógica cacheada."""
    return _obtener_anuncios_logic(keyword, country, max_cards)

# ==========================================
# INTERFAZ STREAMLIT
# ==========================================

st.title("🚀 Mega Buscador PEV (Refactorizado)")
st.markdown("### *Metodología de Espionaje Viral Mejorada y Optimizada*")

st.sidebar.header("🎯 METODOLOGÍA CRISTIAN")
st.sidebar.info("Esta versión incluye mejoras de rendimiento y usabilidad.")

menu = st.sidebar.radio("Selecciona una opción:", [
    "🚀 Guía de Inicio Rápido", "📊 Demanda por País (Mejorado)", "💡 Frases Clave Cristian", 
    "🔎 Búsqueda General", "🔬 Análisis Profundo (Viralidad)", "🕵️‍♂️ Análisis de Competidores", 
    "🧮 Calculadora de Rentabilidad", "📋 Checklist del Proceso", "🎯 Nichos de Alto Rendimiento"
])

# Botón para cerrar el driver en la barra lateral
st.sidebar.button("Terminar Sesión y Cerrar Navegador", on_click=quit_session_driver, type="secondary")


# ==========================================
# MÓDULOS DE LA APLICACIÓN (Selección del Menú)
# ==========================================

if menu == "🚀 Guía de Inicio Rápido":
    # ... (Sin cambios en esta sección, es contenido estático) ...
    st.header("🚀 Guía de Inicio Rápido - Metodología Cristian")
    st.markdown("...") # Contenido de la guía

elif menu == "📊 Demanda por País (Mejorado)":
    st.header("📊 Análisis de Demanda por País - Con Priorización por Tiers")
    
    # ... (sin cambios en la visualización de Tiers) ...
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🔥 TIER-1 (Prioridad Máxima)")
        st.json(COUNTRY_TIERS['tier_1'], expanded=False)
    with col2:
        st.markdown("### ⭐ TIER-2 (Alta Prioridad)")
        st.json(COUNTRY_TIERS['tier_2'], expanded=False)
    with col3:
        st.markdown("### 📝 TIER-3 (Prioridad Moderada)")
        st.json(COUNTRY_TIERS['tier_3'], expanded=False)
    st.markdown("---")

    # MEJORA: Mostrar resultados previos si existen en la sesión
    if 'demand_results_df' in st.session_state:
        st.markdown("### 📈 Resultados del Último Análisis")
        st.dataframe(st.session_state.demand_results_df, use_container_width=True)
        # Re-generar gráfico
        df_chart = st.session_state.demand_results_df.sort_values("Anuncios", ascending=False).head(20)
        fig, ax = plt.subplots(figsize=(12, 8))
        tier_colors = {"TIER_1": "#ff4444", "TIER_2": "#ffaa44", "TIER_3": "#44aaff", "UNKNOWN": "#cccccc"}
        colors = [tier_colors.get(tier.upper(), "#cccccc") for tier in df_chart["Tier"]]
        ax.barh(df_chart["País"] + " - " + df_chart["Keyword"], df_chart["Anuncios"], color=colors)
        ax.invert_yaxis()
        ax.set_xlabel("Número de Anuncios")
        ax.set_title("Top 20 Demanda por País y Keyword")
        st.pyplot(fig)
        st.markdown("---")

    # Configuración de búsqueda
    col1, col2 = st.columns([2, 3])
    with col1:
        # ... (sin cambios en la UI de selección) ...
        idioma_base = st.selectbox("Idioma base:", list(LANGS.keys()), key="demand_lang")
        keywords_input = st.text_area("Keywords/Frases (separadas por coma):", "acceso inmediato a, guía completa, descargar ahora gratis", key="demand_kw")

    with col2:
        # ... (sin cambios en la UI de selección) ...
        include_tier1 = st.checkbox("🔥 Incluir TIER-1", value=True, key="d_t1")
        include_tier2 = st.checkbox("⭐ Incluir TIER-2", value=False, key="d_t2")
        include_tier3 = st.checkbox("📝 Incluir TIER-3", value=False, key="d_t3")
        # ... Lógica para construir paises_selected ...
        paises_selected = []
        if include_tier1: paises_selected.extend(COUNTRY_TIERS["tier_1"]["countries"])
        if include_tier2: paises_selected.extend(COUNTRY_TIERS["tier_2"]["countries"])
        if include_tier3: paises_selected.extend(COUNTRY_TIERS["tier_3"]["countries"])
        paises_final = st.multiselect("Países a analizar:", ALL_COUNTRIES, default=list(set(paises_selected)), format_func=lambda x: f"{x} - {COUNTRY2NAME[x]}")

    traducir_auto = st.checkbox("Traducir automáticamente", value=True, key="demand_translate")
    
    if st.button("🔍 Medir Demanda", type="primary"):
        if keywords_input and paises_final:
            driver = get_session_driver() # Inicia el driver si no existe
            if driver:
                keywords = [kw.strip() for kw in keywords_input.split(",")]
                
                progress_bar = st.progress(0, text="Iniciando análisis...")
                resultados = []
                total_jobs = len(paises_final)
                
                for i, pais in enumerate(paises_final):
                    progress_text = f"Analizando {COUNTRY2NAME[pais]} ({pais})... ({i+1}/{total_jobs})"
                    progress_bar.progress((i + 1) / total_jobs, text=progress_text)
                    
                    tier_info = get_country_tier_info(pais)
                    # Lógica de traducción aquí
                    idioma_pais = next((lang for lang, paises in [("portuguese", PAISES_PORTUGUESE), ("english", PAISES_ENGLISH), ("french", PAISES_FRENCH), ("german", PAISES_GERMAN)] if pais in paises), "spanish")
                    keywords_traducidas = traducir_palabras(tuple(keywords), idioma_pais) if traducir_auto else keywords

                    for keyword in keywords_traducidas:
                        count = count_ads_quick(keyword, pais)
                        if count > 0: # Solo agregar si hay resultados
                            viral_status = validate_viral_offer(count, 0)
                            resultados.append({
                                "País": COUNTRY2NAME[pais], "Código": pais, "Tier": tier_info["tier"], 
                                "Prioridad": tier_info["priority"], "Keyword": keyword, "Anuncios": count,
                                "Estado Viral": viral_status["status"], "Acción": viral_status["action"]
                            })
                
                progress_bar.empty()
                if resultados:
                    df = pd.DataFrame(resultados)
                    tier_order = {"tier_1": 1, "tier_2": 2, "tier_3": 3, "unknown": 4}
                    df["Orden"] = df["Tier"].map(tier_order)
                    df = df.sort_values(["Orden", "Anuncios"], ascending=[True, False]).drop("Orden", axis=1)
                    
                    st.session_state.demand_results_df = df # MEJORA: Guardar en sesión
                    st.rerun() # Volver a correr el script para mostrar los resultados al inicio
                else:
                    st.warning("No se encontraron anuncios para los criterios seleccionados.")
        else:
            st.error("Por favor, ingresa keywords y selecciona países.")

# ... resto de los módulos ...
# Para los demás módulos, la idea es similar:
# 1. Llamar a `get_session_driver()` al inicio de una operación de scraping.
# 2. Usar las funciones refactorizadas que aceptan el `driver` o que ya lo usan internamente.
# 3. Guardar resultados importantes en `st.session_state` para persistencia.
# 4. Reemplazar HTML inseguro por componentes de Streamlit.

elif menu == "🔬 Análisis Profundo (Viralidad)":
    st.header("🔬 Análisis Profundo - Detector de Viralidad")
    # ... (contenido estático) ...

    url_analisis = st.text_input("URL de Facebook Ads Library:", placeholder="https://www.facebook.com/ads/library/?...")
    
    if st.button("🔬 Analizar Viralidad", type="primary"):
        if url_analisis:
            driver = get_session_driver()
            if driver:
                with st.spinner("Analizando página... Esto puede tomar unos minutos"):
                    driver.get(url_analisis)
                    # ... Lógica de scroll ...
                    st.write("Cargando contenido...")
                    for _ in range(5):
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)

                    # ... Lógica de extracción de tarjetas ...
                    cards = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='ad-library-card']")
                    st.success(f"📊 Encontradas {len(cards)} tarjetas de anuncio")

                    # MEJORA: Usar st.container en lugar de HTML inseguro
                    # (Lógica para procesar las tarjetas y encontrar duplicados)
                    contenidos = {}
                    anuncios_procesados = []
                    # ... (código para rellenar anuncios_procesados) ...

                    # Ejemplo de cómo mostrar un resultado
                    for anuncio in sorted(anuncios_procesados, key=lambda x: x["Duplicaciones"], reverse=True):
                        with st.container(border=True):
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                st.metric(label="Duplicaciones", value=anuncio['Duplicaciones'])
                                st.markdown(f"**{anuncio['Color']} {anuncio['Complejidad']}**")
                            with col2:
                                st.markdown(f"**Copy:** {anuncio['Copy'][:250]}...")
                                st.info(f"**Recomendación:** {anuncio['Recomendación']}")
        else:
            st.error("Por favor, ingresa una URL válida")
            
# AÑADIR UN RECORDATORIO PARA EL requirements.txt
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Dependencias")
st.sidebar.code("""
# requirements.txt
streamlit
pandas
matplotlib
selenium
deep-translator
""")
st.sidebar.markdown("Ejecuta `pip install -r requirements.txt` para instalar.")