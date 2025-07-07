# mega_recontrabuscador.py
# 100% SCRAPING REAL · Facebook Ads Library · MVP PRO
# Requisitos:
# pip install -U streamlit selenium pandas matplotlib deep-translator
# Descarga el ChromeDriver correcto: https://chromedriver.chromium.org/downloads

import os, time, re, random, pandas as pd, streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from urllib.parse import quote
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from deep_translator import GoogleTranslator

#───────────────────────────── CONSTANTES ─────────────────────────────#
st.set_page_config(page_title="Mega Buscador PEV", layout="wide")

LANGS = [
    "Español","Inglés","Portugués","Francés","Alemán","Holandés",
    "Italiano","Chino","Hindi","Japonés","Coreano","Indonesio","Árabe"
]
LANG2ISO = {
    "Español":"es","Inglés":"en","Portugués":"pt","Francés":"fr","Alemán":"de","Holandés":"nl",
    "Italiano":"it","Chino":"zh-CN","Hindi":"hi","Japonés":"ja","Coreano":"ko","Indonesio":"id","Árabe":"ar"
}
PAISES_ESP = ["MX","ES","AR","CO","CL","PE"]
PAISES_ENG = ["US","GB","CA","AU","NZ"]
PAISES_PT = ["BR"]
PAISES_FR = ["FR"]
PAISES_DE = ["DE"]
PAISES_NL = ["NL"]
PAISES_IT = ["IT"]
PAISES_CN = ["CN"]
PAISES_HI = ["IN"]
PAISES_JA = ["JP"]
PAISES_KO = ["KR"]
PAISES_ID = ["ID"]
PAISES_AR = ["EG","MA"]
COUNTRY2NAME = {
    "US":"Estados Unidos","CA":"Canadá","MX":"México","GB":"Reino Unido","DE":"Alemania","ES":"España",
    "NL":"Países Bajos","FR":"Francia","CN":"China","IN":"India","JP":"Japón","KR":"Corea del Sur",
    "ID":"Indonesia","BR":"Brasil","AR":"Argentina","CO":"Colombia","CL":"Chile","PE":"Perú","AU":"Australia",
    "NZ":"Nueva Zelanda","ZA":"Sudáfrica","NG":"Nigeria","KE":"Kenia","EG":"Egipto","MA":"Marruecos"
}
ALL_COUNTRIES = list(COUNTRY2NAME.keys())
LANG_DEFAULT = {
    "Español":PAISES_ESP, "Inglés":PAISES_ENG, "Portugués":PAISES_PT, "Francés":PAISES_FR,
    "Alemán":PAISES_DE, "Holandés":PAISES_NL, "Italiano":PAISES_IT, "Chino":PAISES_CN,
    "Hindi":PAISES_HI, "Japonés":PAISES_JA, "Coreano":PAISES_KO, "Indonesio":PAISES_ID, "Árabe":PAISES_AR
}
UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/126",
    "Mozilla/5.0 (Macintosh) Safari/605.1.15"
]

#───────────────────────────── FUNCIONES ─────────────────────────────#

def get_driver(incognito=False):
    opts = ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument(f"--user-agent={random.choice(UA_LIST)}")
    if incognito: opts.add_argument("--incognito")
    return Chrome(options=opts)

def traducir_palabras(palabras, idioma_destino):
    traducidas = []
    for p in palabras:
        try:
            traducidas.append(GoogleTranslator(source='auto', target=idioma_destino).translate(p))
        except: traducidas.append(p)
        time.sleep(0.5)
    return traducidas

def count_ads_quick(keyword:str, country:str) -> int:
    driver = get_driver()
    url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={quote(keyword)}"
    driver.get(url)
    try:
        txt = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.XPATH,"//div[contains(text(),' result')]"))
        ).text
        return int(re.sub(r"[^\d]","",txt))
    except: return 0
    finally:
        driver.quit()
        time.sleep(0.5)

def obtener_anuncios(keyword, country, max_cards=10):
    driver = get_driver()
    url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={quote(keyword)}"
    driver.get(url)
    time.sleep(2)
    anuncios = []
    try:
        cards = driver.find_elements(By.CSS_SELECTOR,".x1lliihq")
        for c in cards[:max_cards]:
            try:
                copy = c.text.strip()
                link = c.find_element(By.TAG_NAME,"a").get_attribute("href")
                if len(copy) < 10: continue
                anuncios.append({
                    "País":country,
                    "Copy":copy[:300] + "..." if len(copy)>300 else copy,
                    "Link":link
                })
            except Exception: continue
    except Exception: pass
    driver.quit()
    return anuncios

def color_duplicado(n): return "red" if n>=5 else "yellow" if n>=3 else "purple"

#───────────────────────────── MENÚ LATERAL ─────────────────────────────#
st.sidebar.title("Selecciona una tarea:")
menu = st.sidebar.radio(
    "", [
        "🚀 Guía de Inicio Rápido",
        "📊 Demanda por País",
        "💡 Inspiración de Keywords",
        "🔎 Búsqueda General por Palabras Clave",
        "🔬 Análisis Profundo de Página de Resultados",
        "🕵️‍♂️ Análisis Específico de Competidores",
        "🧮 Calculadora de Rentabilidad",
        "📋 Checklist del Proceso"
    ]
)

#───────────────────────────── MENÚ PRINCIPAL ─────────────────────────────#

# ────────────── 1. DEMANDA POR PAÍS ──────────────
if menu=="📊 Demanda por País":
    st.header("📊 Demanda por País")
    idioma = st.selectbox("Idioma base", LANGS, key="idioma_demanda")
    palabras = st.text_area("Keywords (coma-separadas)", key="kw_demanda")
    paises = st.multiselect(
        "Países destino", ALL_COUNTRIES, default=LANG_DEFAULT.get(idioma,[]), key="paises_demanda"
    )
    traducir = st.checkbox("Traducir automáticamente", value=True)
    col1, col2 = st.columns([2,2])

    if col1.button("Medir demanda"):
        if not palabras or not paises:
            st.error("Debes ingresar palabras y al menos un país.")
        else:
            kws = [k.strip() for k in palabras.split(",") if k.strip()]
            df_out = []
            st.info("Midiendo en Facebook Ads Library (esto puede tardar varios minutos)...")
            for p in paises:
                idioma_pais = LANG2ISO[idioma]
                palabras_final = traducir_palabras(kws, idioma_pais) if traducir else kws
                for k in palabras_final:
                    n = count_ads_quick(k, p)
                    df_out.append({"País":p, "Keyword":k, "Anuncios":n})
            df = pd.DataFrame(df_out)
            st.dataframe(df)
            # Gráfico de barras
            graf = df.groupby("País")["Anuncios"].sum().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(8, max(3, len(graf)//2)))
            graf.plot(kind="barh", ax=ax)
            ax.set_title(f"Demanda de '{palabras}'")
            ax.invert_yaxis()
            plt.tight_layout()
            st.pyplot(fig)

    if col2.button("→Enviar a Búsqueda"):
        if not paises:
            st.error("Debes seleccionar al menos un país destino.")
        else:
            st.session_state["paises_busqueda"] = paises
            st.success("Países enviados a búsqueda general. Ve al menú '🔎 Búsqueda General...'")

    # BLOQUE WORKFLOW PRO SIEMPRE VISIBLE
    st.markdown("""
<div class="workflow-pro">
<strong>Workflow pro:</strong><br>
<span class="emoji">1️⃣</span> Juega con <strong>“Demanda”</strong> hasta ver dónde hay +5 000 anuncios.<br>
<span class="emoji">2️⃣</span> Pulsa → <strong>Enviar a Búsqueda</strong> solo para esos países.<br>
<span class="emoji">3️⃣</span> En “Búsqueda General” obtienes ejemplos reales y los filtras con scroll, copy ≥ 100 car., etc.<br>
<br>
<b>Sin rodeos:</b> usa la caja de Keywords, marca “Traducir” si no quieres meter mano en alemán o japonés, y deja que el botón te haga el trabajo sucio. 😊
</div>
    """, unsafe_allow_html=True)

# ────────────── 2. INSPIRACIÓN DE KEYWORDS (PENDIENTE INTEGRACIÓN REAL) ──────────────
elif menu=="💡 Inspiración de Keywords":
    st.header("💡 Inspiración de Keywords")
    st.info("En desarrollo: aquí se integrarán sugerencias automáticas en versión futura.")

# ────────────── 3. BÚSQUEDA GENERAL (PALABRAS CLAVE) ──────────────
elif menu=="🔎 Búsqueda General por Palabras Clave":
    st.header("🔎 Búsqueda General de E-books Ganadores")
    idioma = st.selectbox("Idioma base", LANGS, key="idioma_buscgen")
    paises = st.multiselect(
        "País destino (ISO)", ALL_COUNTRIES, default=st.session_state.get("paises_busqueda", []), key="paises_buscgen"
    )
    palabras = st.text_area("Keywords (coma-separadas)", key="kw_buscgen")
    min_ads = st.number_input("Mín anuncios 'ganador'", 1, 100, value=30)
    if st.button("Iniciar búsqueda"):
        if not paises or not palabras:
            st.warning("Debes seleccionar países y palabras clave.")
        else:
            kws = [k.strip() for k in palabras.split(",") if k.strip()]
            for p in paises:
                idioma_pais = LANG2ISO[idioma]
                palabras_final = traducir_palabras(kws, idioma_pais)
                st.markdown(f"### {COUNTRY2NAME.get(p,p)} ({p})")
                for k in palabras_final:
                    st.markdown(f"**Keyword:** {k}")
                    anuncios = obtener_anuncios(k, p, max_cards=5)
                    if anuncios:
                        df = pd.DataFrame(anuncios)
                        st.dataframe(df)
                    else:
                        st.info("No se encontraron anuncios para esta palabra.")

# ────────────── 4. ANÁLISIS PROFUNDO DE PÁGINA DE RESULTADOS ──────────────
elif menu=="🔬 Análisis Profundo de Página de Resultados":
    st.header("🔬 Análisis Profundo de Página de Resultados")
    url = st.text_input("URL de página de resultados de Facebook Ads Library")
    min_copies = st.number_input("Mínimo de réplicas por creatividad", min_value=1, value=3)
    if st.button("Analizar página"):
        if not url:
            st.warning("Ingresa una URL válida.")
        else:
            driver = get_driver()
            driver.get(url)
            time.sleep(2)
            cards = driver.find_elements(By.CSS_SELECTOR, ".x1lliihq")
            counts = {}
            infos = []
            for c in cards:
                cid = c.get_attribute('id') or c.text[:120]
                counts[cid] = counts.get(cid, 0) + 1
                infos.append((cid, c.text, c.find_element(By.TAG_NAME, "a").get_attribute("href") if c.find_elements(By.TAG_NAME, "a") else url))
            driver.quit()
            st.write("Creatividades replicadas (TOP):")
            for cid, text, link in sorted(infos, key=lambda x: counts[x[0]], reverse=True):
                if counts[cid] >= min_copies:
                    st.markdown(f"<div style='border:2px solid {color_duplicado(counts[cid])};padding:8px;border-radius:4px;margin-bottom:4px;'>{text[:300]}<br><a href='{link}' target='_blank'>Ver anuncio</a></div>", unsafe_allow_html=True)

# ────────────── 5. ANÁLISIS ESPECÍFICO DE COMPETIDORES ──────────────
elif menu=="🕵️‍♂️ Análisis Específico de Competidores":
    st.header("🕵️‍♂️ Análisis Específico de Competidores")
    comp = st.text_area("Competidores (separados por comas)")
    pais = st.selectbox("País/Región", ALL_COUNTRIES)
    if st.button("Analizar Competidores"):
        comps = [c.strip() for c in comp.split(",") if c.strip()]
        for page in comps:
            url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={pais}&q={quote(page)}"
            driver = get_driver()
            driver.get(url)
            time.sleep(2)
            try:
                txt = WebDriverWait(driver,10).until(
                    EC.presence_of_element_located((By.XPATH,"//div[contains(text(),' result')]"))
                ).text
                total = int(re.sub(r"[^\d]","",txt))
            except:
                total = 0
            driver.quit()
            st.markdown(f"**{page}:** {total} anuncios activos e inactivos - [Ver en Facebook Ads Library]({url})")

# ────────────── 6. CALCULADORA DE RENTABILIDAD ──────────────
elif menu=="🧮 Calculadora de Rentabilidad":
    st.header("🧮 Calculadora de Rentabilidad")
    precio = st.number_input("Precio de venta (USD)", value=19.0)
    cpa = st.number_input("Costo por Adquisición (USD)", value=3.5)
    ventas = st.number_input("Ventas estimadas", value=100)
    if st.button("Calcular"):
        ganancia = (precio-cpa)*ventas
        st.success(f"Ganancia estimada: ${ganancia:,.2f} USD")

# ────────────── 7. CHECKLIST DEL PROCESO ──────────────
elif menu=="📋 Checklist del Proceso":
    st.header("📋 Checklist del Proceso")
    steps = [
        "☑️ Medir demanda en Facebook Ads",
        "☑️ Seleccionar países 'hot'",
        "☑️ Buscar copys ganadores",
        "☑️ Analizar competidores",
        "☑️ Calcular rentabilidad",
        "☑️ Lanzar campaña y optimizar"
    ]
    st.write("\n".join(steps))
    st.success("¡Checklist completado para el MVP!")

# ────────────── 0. GUÍA DE INICIO RÁPIDO ──────────────
else:
    st.header("🚀 Guía de Inicio Rápido")
    st.markdown("""
1. Ve a **Demanda por País** y mide anuncios para tus palabras clave.
2. Selecciona los países “calientes” y pulsa **Enviar a Búsqueda**.
3. Busca los anuncios ganadores y copia keywords para nuevos productos.
    """)

#───────────────────────────── FIN DEL SCRIPT ─────────────────────────────#
