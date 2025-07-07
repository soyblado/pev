# dashboard_app.py
# VERSIÓN FINAL, COMPLETA Y FUNCIONAL - REINO UNIDO AÑADIDO

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

# --- PARÁMETROS GLOBALES ---
BASE_URL = 'https://www.facebook.com/ads/library/'
TARGET_COUNTRIES_WITH_LANG = {
    'CO': ('Colombia', 'es'),
    'ES': ('España', 'es'),
    'MX': ('México', 'es'),
    'US': ('Estados Unidos', 'en'),
    'GB': ('Reino Unido', 'en'), # <-- AÑADIDO
    'BR': ('Brasil', 'pt'),
    'FR': ('Francia', 'fr')
}
DEFAULT_KEYWORDS_BY_LANG = {
    'es': ['libro electronico', 'guia digital', 'desarrollo personal', 'espiritualidad'],
    'en': ['ebook', 'digital guide', 'personal development', 'spirituality'],
    'pt': ['livro digital', 'guia digital', 'desenvolvimento pessoal', 'espiritualidade'],
    'fr': ['livre numérique', 'guide numérique', 'développement personnel', 'spiritualité']
}
RESULTS_TEXT_XPATH = '//div[contains(text(), " resultado") or contains(text(), " result")]'
AD_CARD_SELECTOR_XPATH = "//div[contains(@class, 'x1yztbdb') and contains(@class, 'x1n2onr6') and contains(@class, 'xh8yej3') and contains(@class, 'x1ja2u2z')]"

# --- FUNCIONES DE LÓGICA ---
# @st.cache_resource
def get_driver():
    return webdriver.Chrome()

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
                    winners.append({"text": ad_text, "copies": num_copies})
        return winners
    except Exception as e:
        st.error(f"Ocurrió un error al analizar la página. Error: {e}")
        return []

def create_checklist_html():
    html_content = """
    <!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Checklist del Proceso</title><style>body{font-family:sans-serif;margin:40px;line-height:1.6;}h1,h2{color:#0c4a6e;}h2{border-bottom:2px solid #e0f2fe;padding-bottom:10px;margin-top:40px;}ul{list-style-type:'✅ ';padding-left:20px;}li{margin-bottom:10px;}strong{color:#075985;}code{background-color:#f8fafc;padding:2px 6px;border-radius:4px;font-family:monospace;}</style></head>
    <body><h1>✅ Checklist: Proceso de Investigación de Principio a Fin</h1><p>Usa esta hoja de ruta cada vez que inicies la búsqueda de un nuevo producto.</p>
    <h2>Paso 1: Búsqueda General por Palabras Clave</h2><ul><li><strong>Objetivo:</strong> Encontrar un mercado "caliente" con alta demanda.</li><li><strong>Acción:</strong> Busca hasta encontrar un ¡ÉXITO! con +50 anuncios y <strong>guarda el enlace</strong> de resultados.</li></ul>
    <h2>Paso 2: Análisis Profundo de Página de Resultados</h2><ul><li><strong>Objetivo:</strong> Encontrar el creativo exacto más exitoso de la competencia.</li><li><strong>Acción:</strong> Pega la URL del Paso 1 en esta herramienta. El panel te mostrará el anuncio más duplicado. <strong>Anota el nombre del anunciante</strong>.</li></ul>
    <h2>Paso 3: Análisis Específico de Competidores</h2><ul><li><strong>Objetivo:</strong> Ver todo el arsenal de anuncios y estrategias de tu competidor principal.</li><li><strong>Acción:</strong> Pega el nombre de la Página de Facebook del Paso 2 para ver todos los anuncios de ese competidor.</li></ul>
    <h2>Paso 4: Análisis de Viabilidad Financiera</h2><ul><li><strong>Objetivo:</strong> Decidir si el producto es rentable para ti <em>antes</em> de invertir más tiempo.</li><li><strong>Acción:</strong> Haz "Funnel Hacking" manual en los anuncios para <strong>descubrir el precio del producto</strong>. Luego, introduce ese precio en la Calculadora para obtener tu <strong>CPA Máximo</strong>.</li></ul>
    <h2>Paso 5: Modelado y Lanzamiento</h2><ul><li><strong>Objetivo:</strong> Salir al mercado con tu propia oferta validada.</li><li><strong>Acción:</strong> Con toda la inteligencia reunida, modela tu oferta. Lanza tu campaña usando tu <strong>CPA Máximo</strong> del Paso 4 como guía para tu presupuesto diario.</li></ul>
    </body></html>
    """
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

# --- BLOQUES COMPLETOS Y FUNCIONALES ---

if app_mode == "🚀 Guía de Inicio Rápido":
    st.header("🏁 Guía de Inicio Rápido: Tu Flujo de Trabajo Correcto")
    st.info("Esta guía te orienta sobre cómo usar las herramientas del panel en el orden lógico para maximizar tus resultados.")
    st.subheader("Paso 1: Búsqueda General por Palabras Clave")
    st.markdown("Empieza aquí para encontrar un nicho o mercado con alta demanda. Tu objetivo es encontrar una palabra clave con más de 50 anuncios activos.")
    st.subheader("Paso 2: Análisis Profundo de Página de Resultados")
    st.markdown("Una vez que encuentres una página de resultados interesante en el Paso 1, usa esta herramienta para escanearla y encontrar el anuncio específico más viral y a su anunciante.")
    st.subheader("Paso 3: Análisis Específico de Competidores")
    st.markdown("Con el nombre del anunciante que encontraste en el Paso 2, usa esta herramienta para investigar todo su arsenal de anuncios y estrategias.")
    st.subheader("Paso 4: Calculadora de Rentabilidad")
    st.markdown("Antes de modelar, haz un espionaje manual en las páginas de venta de tu competidor para averiguar el precio del producto. Luego, ven a esta herramienta, introduce los datos y calcula tu CPA Máximo para ver si el negocio es viable.")
    st.subheader("Paso 5: Checklist del Proceso y Lanzamiento")
    st.markdown("Finalmente, abre el checklist para repasar todos los pasos y asegurarte de que no te olvidas de nada antes de modelar tu oferta y lanzar tu campaña.")
    st.markdown("---")
    checklist_href = create_checklist_html()
    st.link_button("📜 Abrir Checklist Detallado en una Nueva Pestaña", url=checklist_href)

elif app_mode == "🔎 Búsqueda General por Palabras Clave":
    st.header("🔎 Búsqueda General de E-books Ganadores")
    st.info("Introduce palabras clave por idioma. El script buscará automáticamente cada palabra en los países que correspondan a ese idioma.")
    min_ads_input = st.number_input("Mínimo de anuncios para ser 'ganador':", min_value=1, value=15)
    with st.expander("📝 Palabras Clave en Español (para CO, ES, MX)"):
        es_keywords_text = st.text_area("Español:", value="\n".join(DEFAULT_KEYWORDS_BY_LANG['es']), height=150)
    with st.expander("📝 Palabras Clave en Inglés (para US, GB)"):
        en_keywords_text = st.text_area("Inglés:", value="\n".join(DEFAULT_KEYWORDS_BY_LANG['en']), height=150)
    with st.expander("📝 Palabras Clave en Portugués (para BR)"):
        pt_keywords_text = st.text_area("Portugués:", value="\n".join(DEFAULT_KEYWORDS_BY_LANG['pt']), height=150)
    with st.expander("📝 Palabras Clave en Francés (para FR)"):
        fr_keywords_text = st.text_area("Francés:", value="\n".join(DEFAULT_KEYWORDS_BY_LANG['fr']), height=150)
    
    if st.button("🚀 Iniciar Búsqueda Inteligente"):
        keywords_by_lang_input = {
            'es': [line.strip() for line in es_keywords_text.split('\n') if line.strip()],
            'en': [line.strip() for line in en_keywords_text.split('\n') if line.strip()],
            'pt': [line.strip() for line in pt_keywords_text.split('\n') if line.strip()],
            'fr': [line.strip() for line in fr_keywords_text.split('\n') if line.strip()],
        }
        driver = get_driver()
        st.info("Driver iniciado. ¡Comenzando la búsqueda inteligente!")
        results_container = st.container()
        for country_code, (country_name, lang_code) in TARGET_COUNTRIES_WITH_LANG.items():
            keywords_for_this_country = keywords_by_lang_input.get(lang_code, [])
            if not keywords_for_this_country:
                continue
            st.write(f"--- Analizando **{country_name.upper()}** con palabras clave en **{lang_code.upper()}** ---")
            for keyword in keywords_for_this_country:
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

elif app_mode == "🔬 Análisis Profundo de Página de Resultados":
    st.header("🔬 Análisis Profundo de Página de Resultados")
    st.info("Pega la URL de una página de resultados para extraer las creatividades que más se repiten.")
    page_url_input = st.text_input("URL de la página de resultados a analizar:", placeholder="https://www.facebook.com/ads/library/?q=...")
    min_copies_input = st.number_input("Número mínimo de 'copias' para ser un ganador:", min_value=1, value=10)
    if st.button("🧠 Iniciar Análisis Profundo"):
        if not page_url_input.strip().startswith("http"):
            st.warning("Por favor, introduce una URL válida.")
        else:
            driver = get_driver()
            st.info("Iniciando análisis profundo...")
            winners = analyze_page_for_copies(driver, page_url_input, min_copies_input)
            if winners:
                st.success(f"¡Análisis completado! Se encontraron {len(winners)} anuncios ganadores.")
                for winner in sorted(winners, key=lambda x: x['copies'], reverse=True):
                    with st.expander(f"GANADOR: {winner['copies']} copias encontradas"):
                        st.code(winner['text'], language=None)
            else:
                st.warning("No se encontraron anuncios que cumplieran el criterio.")
            st.balloons()
            st.header("¡Análisis profundo finalizado!")
            driver.quit()

elif app_mode == "🕵️ Análisis Específico de Competidores":
    st.header("🕵️ Análisis Específico de Competidores")
    st.info("Investiga a un competidor a través de su nombre de Página de Facebook o su dominio web.")
    advertisers_input = st.text_area("Introduce una lista de anunciantes o dominios (uno por línea):", height=150, placeholder="Nombre de Página\nejemplo.com")
    if st.button("🔬 Iniciar Análisis Específico"):
        if not advertisers_input.strip():
            st.warning("Por favor, introduce al menos un anunciante.")
        else:
            driver = get_driver()
            st.info("Iniciando análisis...")
            targets = [line.strip() for line in advertisers_input.split('\n') if line.strip()]
            for target in targets:
                with st.expander(f"Resultados para: '{target}'"):
                    st.write(f"Investigando a **{target}** en todos los países...")
                    for country_code, (country_name, lang_code) in TARGET_COUNTRIES_WITH_LANG.items():
                        encoded_target = quote(target)
                        search_url = f"{BASE_URL}?active_status=all&ad_type=all&country={country_code}&q={encoded_target}&search_type=keyword_exact_phrase"
                        num_ads = search_by_url(driver, search_url)
                        if num_ads > 0:
                            st.success(f"**{country_name}:** Encontrados **{num_ads}** anuncios. [Ver aquí]({search_url})")
                        time.sleep(1)
            st.balloons()
            st.header("¡Análisis finalizado!")
            driver.quit()

elif app_mode == "🧮 Calculadora de Rentabilidad":
    st.header("🧮 Calculadora de Rentabilidad y Estrategia")
    st.info("Usa esta herramienta **antes de lanzar tu campaña** para planificar tus finanzas y estrategia.")
    st.subheader("1. Ingresa los datos de tu producto")
    precio_venta = st.number_input("Precio de Venta del Producto ($)", min_value=0.1, value=19.99, step=1.0)
    comision_porc = st.slider("Tu Comisión (%)", min_value=1, max_value=100, value=80)
    tu_ganancia = st.number_input("De tu comisión, ¿cuánto es tu ganancia personal por venta ($)?", min_value=0.0, value=3.0, step=0.5)

    if st.button("Calcular Mis Métricas Clave"):
        comision_valor = precio_venta * (comision_porc / 100.0)
        if tu_ganancia >= comision_valor:
            st.error("Tu ganancia personal no puede ser igual o mayor que el valor total de la comisión.")
        else:
            ingreso_neto_negocio = comision_valor - tu_ganancia
            st.subheader("✅ Tus Números Clave para la Campaña")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="CPA Máximo (Breakeven)", value=f"${ingreso_neto_negocio:.2f}", help="Costo máximo que puedes pagar por una venta para no perder dinero.")
            roas_limite = precio_venta / ingreso_neto_negocio if ingreso_neto_negocio > 0 else 0
            with col2:
                st.metric(label="ROAS Límite (Breakeven)", value=f"{roas_limite:.2f}", help="Retorno de inversión mínimo que necesitas.")
    st.markdown("---")
    st.subheader("Manual de Acción: Cómo Usar Tus Números")
    st.markdown("* **Presupuesto Diario:** Establece el presupuesto diario igual a tu 'CPA Máximo'.\n* **Regla de Gasto:** Si el gasto alcanza tu 'CPA Máximo' sin ventas, apaga la campaña.\n* **Regla de ROAS:** Si el ROAS está por debajo de tu 'ROAS Límite', la campaña pierde dinero.\n* **Regla de Tiempo:** Si una campaña lleva 2 días sin vender, apágala.\n* **Paciencia:** No hagas cambios antes de 24 horas o 2,000 impresiones.")

elif app_mode == "📜 Checklist del Proceso":
    st.header("✅ Checklist: Proceso de Investigación de Principio a Fin")
    st.info("Usa esta hoja de ruta cada vez que inicies la búsqueda de un nuevo producto.")
    st.subheader("Paso 1: Búsqueda General por Palabras Clave")
    st.markdown("- **Herramienta a Usar:** `🔎 Búsqueda General por Palabras Clave`.\n- **Acción:** Busca hasta encontrar un `¡ÉXITO!` con +50 anuncios y guarda el enlace de resultados.")
    st.subheader("Paso 2: Análisis Profundo de Página de Resultados")
    st.markdown("- **Herramienta a Usar:** `🔬 Análisis Profundo de Página de Resultados`.\n- **Acción:** Pega la URL del Paso 1 para encontrar el anuncio más duplicado y **anota el nombre del anunciante**.")
    st.subheader("Paso 3: Análisis Específico de Competidores")
    st.markdown("- **Herramienta a Usar:** `🕵️ Análisis Específico de Competidores`.\n- **Acción:** Pega el nombre del anunciante del Paso 2 para ver todo su arsenal de anuncios.")
    st.subheader("Paso 4: Análisis de Viabilidad Financiera")
    st.markdown("- **Herramienta a Usar:** `🧮 Calculadora de Rentabilidad`.\n- **Acción:** Haz \"Funnel Hacking\" manual en los anuncios para **descubrir el precio del producto**. Luego, introduce ese precio en la Calculadora para obtener tu **CPA Máximo**.")
    st.subheader("Paso 5: Modelado y Lanzamiento")
    st.markdown("- **Herramienta a Usar:** Manual.\n- **Acción:** Con toda la inteligencia reunida, modela tu oferta. Lanza tu campaña usando tu **CPA Máximo** del Paso 4 como guía para tu presupuesto diario.")