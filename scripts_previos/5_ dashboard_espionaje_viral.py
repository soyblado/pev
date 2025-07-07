import streamlit as st
import re
import time
from datetime import datetime
from urllib.parse import quote
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

# ---------------- Funciones de Web Scraping ----------------
def color_duplicado(n):
    """Devuelve el color CSS según número de duplicaciones."""
    if n >= 5:
        return 'red'
    if n >= 3:
        return 'yellow'
    return 'purple'

def espionaje_viral_facebook(
    phrases, country, incognito,
    load_more=False, all_months=False,
    apply_filter=False, page_limit=3,
    remove_hidden=False
):
    """Realiza espionaje viral en Facebook Ads Library con control de duplicados."""
    if 'seen_ads' not in st.session_state:
        st.session_state['seen_ads'] = set()
    if 'recent_links' not in st.session_state:
        st.session_state['recent_links'] = []

    opts = ChromeOptions()
    if incognito:
        opts.add_argument("--incognito")
    driver = Chrome(options=opts)

    xpath_total = "//div[contains(text(), ' result')]"
    since = until = None
    if not all_months:
        today = datetime.today()
        since = f"{today.year}-{today.month:02d}-01"
        until = f"{today.year}-{today.month:02d}-{today.day:02d}"

    resultados = []
    for phrase in phrases:
        url = (
            f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}"
            + (f"&since={since}&until={until}" if since else "")
            + f"&q={quote(phrase)}"
        )
        driver.get(url)
        time.sleep(2)

        if load_more:
            for _ in range(page_limit):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

        try:
            elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath_total))
            )
            total_ads = int(re.sub(r'[^\d]', '', elem.text))
        except:
            total_ads = 0

        cards = driver.find_elements(By.CSS_SELECTOR, ".x1lliihq")
        card_infos = []
        for c in cards:
            try:
                cid = c.get_attribute('id') or c.text[:100]
                text = c.text
            except StaleElementReferenceException:
                continue

            try:
                detail_btn = c.find_element(By.CSS_SELECTOR, "a[href*='ads/library/?id=']")
                link = detail_btn.get_attribute('href')
            except:
                try:
                    link = c.find_element(By.TAG_NAME, 'a').get_attribute('href')
                except:
                    link = url

            card_infos.append({'id': cid, 'text': text, 'link': link})

        counts = {}
        for info in card_infos:
            counts[info['id']] = counts.get(info['id'], 0) + 1

        ejemplos = []
        for cid, cnt in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            if remove_hidden and cid in st.session_state['seen_ads']:
                continue
            sample_text = next(i['text'] for i in card_infos if i['id'] == cid)
            if apply_filter and len(sample_text) < 100:
                continue
            info = next(i for i in card_infos if i['id'] == cid)
            ejemplos.append({'text': info['text'], 'count': cnt, 'link': info['link']})
            st.session_state['seen_ads'].add(cid)
            if len(ejemplos) >= 5:
                break

        resultados.append({'frase': phrase, 'total_ads': total_ads, 'ejemplos': ejemplos, 'link': url})
        st.session_state['recent_links'].append(url)

    driver.quit()
    return resultados

def analisis_profundo_facebook(url, min_copies=1, incognito=False):
    """Analiza creatividades replicadas de una búsqueda o anuncio concreto."""
    opts = ChromeOptions()
    if incognito:
        opts.add_argument("--incognito")
    driver = Chrome(options=opts)
    driver.get(url)
    time.sleep(2)

    cards = driver.find_elements(By.CSS_SELECTOR, ".x1lliihq")
    counts = {}
    for c in cards:
        cid = c.get_attribute('id') or c.text[:100]
        counts[cid] = counts.get(cid, 0) + 1

    resultados = []
    for cid, cnt in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        if cnt < min_copies:
            continue
        card_el = next((c for c in cards if (c.get_attribute('id') or c.text[:100]) == cid), None)
        text = card_el.text if card_el else ''
        try:
            detail_btn = card_el.find_element(By.CSS_SELECTOR, "a[href*='ads/library/?id=']")
            link = detail_btn.get_attribute('href')
        except:
            try:
                link = card_el.find_element(By.TAG_NAME, 'a').get_attribute('href')
            except:
                link = url
        resultados.append({'text': text, 'count': cnt, 'link': link})

    driver.quit()
    return resultados

def analisis_competidores_facebook(pages, country, incognito=False):
    """Analiza anuncios activos e inactivos de páginas competidoras."""
    opts = ChromeOptions()
    if incognito:
        opts.add_argument("--incognito")
    driver = Chrome(options=opts)

    xpath_total = "//div[contains(text(), ' result')]"
    resultados = []
    for page in pages:
        if page.lower().startswith('http'):
            url = page
        else:
            url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={quote(page)}"
        driver.get(url)
        time.sleep(2)
        try:
            elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath_total))
            )
            total = int(re.sub(r'[^\d]', '', elem.text))
        except:
            total = 0
        resultados.append({'page': page, 'total_ads': total, 'link': url})
    driver.quit()
    return resultados

# ---------------- Navegación desde Checklist ----------------
def goto_search():  st.session_state['menu'] = "🔎 Búsqueda General por Palabras Clave"
def goto_deep():    st.session_state['menu'] = "🔬 Análisis Profundo de Página de Resultados"
def goto_comp():    st.session_state['menu'] = "🕵️ Análisis Específico de Competidores"
def goto_calc():    st.session_state['menu'] = "🧮 Calculadora de Rentabilidad"
def goto_check():   st.session_state['menu'] = "📜 Checklist del Proceso"

# ---------------- Interfaz Streamlit ----------------
def main():
    st.set_page_config(page_title="Panel de Control - Investigador de E-books", layout="wide")
    if 'menu' not in st.session_state:
        st.session_state['menu'] = "🚀 Guía de Inicio Rápido"
    menu = st.sidebar.radio(
        "Selecciona una tarea:",
        ["🚀 Guía de Inicio Rápido", "🔎 Búsqueda General por Palabras Clave",
         "🔬 Análisis Profundo de Página de Resultados", "🕵️ Análisis Específico de Competidores",
         "🧮 Calculadora de Rentabilidad", "📜 Checklist del Proceso"],
        key='menu'
    )

    # 1. Guía de Inicio Rápido
    if menu == "🚀 Guía de Inicio Rápido":
        st.title("🚀 Guía de Inicio Rápido: Tu Flujo Correcto")
        st.markdown("1. Búsqueda General\n2. Análisis Profundo\n3. Competidores\n4. Calculadora\n5. Checklist")

    # 2. Búsqueda General
    elif menu == "🔎 Búsqueda General por Palabras Clave":
        st.title("🔎 Búsqueda General de E-books Ganadores")
        if st.button("🔄 Resetear Todo", key="reset_all"):
            for var in ['seen_ads','recent_links','general_results','deep_results','comp_results']:
                st.session_state.pop(var, None)
            st.session_state['menu'] = "🔎 Búsqueda General por Palabras Clave"

        col1, col2 = st.columns(2)
        with col1:
            lang = st.selectbox("Idioma", ["Español","Inglés","Portugués","Francés"], key="lang")
        with col2:
            country_map = {"Español":["CO","ES","MX"],"Inglés":["US","UK"],"Portugués":["BR"],"Francés":["FR"]}
            country = st.selectbox("País/Región", country_map[lang], key="country")

        keywords = st.text_area("Palabras clave (separadas por comas)", key="keywords")
        min_ads = st.number_input("Mínimo de anuncios para ser 'ganador'", min_value=1, value=30, key="min_ads")

        st.markdown("### Controles avanzados")
        c1, c2 = st.columns(2)
        with c1:
            load_ads = st.checkbox("Load Ads automáticamente", key="load_ads")
            all_months = st.checkbox("Todos los meses", key="all_months")
        with c2:
            enable_filter = st.checkbox("Filtro avanzado", key="enable_filter")
            remove_hidden = st.checkbox("Remover vistos", key="remove_hidden")
        page_limit = st.slider("Límite de scroll (páginas)", 1, 10, 5, key="page_limit")

        if st.button("🚀 Iniciar Búsqueda Inteligente", key="start_search"):
            phrases = [p.strip() for p in keywords.split(",") if p.strip()]
            st.session_state['general_results'] = espionaje_viral_facebook(
                phrases, country, incognito=False,
                load_more=load_ads, all_months=all_months,
                apply_filter=enable_filter, page_limit=page_limit,
                remove_hidden=remove_hidden
            )

        if st.session_state.get('general_results'):
            for item in st.session_state['general_results']:
                status = st.success if item['total_ads']>=min_ads else st.info
                status(f"{item['frase']} → {item['total_ads']} anuncios activos")
                st.markdown(f"[🔗 Guardar enlace para análisis profundo]({item['link']})", unsafe_allow_html=True)

    # 3. Análisis Profundo
    elif menu == "🔬 Análisis Profundo de Página de Resultados":
        st.title("🔬 Análisis Profundo de Página de Resultados")
        st.info("Pega aquí una URL directa de anuncio (con ?id=…) o selecciona una búsqueda previa.")
        custom = st.text_input("URL directa de anuncio", key="custom_deep_link")
        options = st.session_state.get('recent_links', [])
        choice = st.selectbox("O elige una búsqueda anterior:", options, key="deep_choice")
        url_to_analyze = custom.strip() if custom.strip() else choice

        min_copies = st.number_input("Mínimo de réplicas por creatividad", min_value=1, value=3, key="deep_min_copies")
        st.caption("3 réplicas = tracción (amarillo), 5 = ganador (rojo)")

        if st.button("🔍 Analizar página", key="start_deep"):
            st.session_state['deep_results'] = analisis_profundo_facebook(url_to_analyze, min_copies, incognito=False)

        if st.session_state.get('deep_results'):
            for i, ex in enumerate(st.session_state['deep_results'], 1):
                col = color_duplicado(ex['count'])
                txt = ex['text'].replace("\n"," ")
                st.markdown(f"<div style='border:2px solid {col}; padding:8px; border-radius:4px; margin-bottom:4px;'>{txt}</div>", unsafe_allow_html=True)
                st.text_input(f"📋 Copiar enlace #{i}", value=ex['link'], key=f"copy_link_{i}")

    # 4. Análisis Competidores
    elif menu == "🕵️ Análisis Específico de Competidores":
        st.title("🕵️ Análisis Específico de Competidores")
        st.info("Ingresa páginas o dominios de competidores para ver sus anuncios.")
        comp = st.text_area("Competidores (separados por comas)")
        country = st.selectbox("País/Región", ["CO","ES","MX","US","UK","BR","FR"], key="comp_country")
        inc = st.checkbox("Abrir en incógnito", value=True, key="comp_incognito")

        if st.button("🔎 Analizar Competidores", key="start_comp"):
            pages = [c.strip() for c in comp.split(",") if c.strip()]
            st.session_state['comp_results'] = analisis_competidores_facebook(pages, country, incognito=inc)

        if st.session_state.get('comp_results'):
            for r in st.session_state['comp_results']:
                st.metric(r['page'], f"{r['total_ads']} anuncios activos e inactivos")
                st.markdown(f"[🔗 Ver en Facebook Ads Library]({r['link']})", unsafe_allow_html=True)

    # 5. Calculadora de Rentabilidad
    elif menu == "🧮 Calculadora de Rentabilidad":
        st.title("🧮 Calculadora de Rentabilidad")
        price = st.number_input("Precio de venta", min_value=0.0, format="%.2f")
        commission = st.number_input("% Comisión", min_value=0.0, format="%.2f")
        profit = st.number_input("Ganancia deseada", min_value=0.0, format="%.2f")
        if st.button("Calcular CPA y ROAS", key="calc_roas"):
            cpa = price * (commission/100)
            roas = price / cpa if cpa else 0
            st.metric("CPA Máximo", f"${cpa:.2f}")
            st.metric("ROAS Límite", f"{roas:.2f}x")
            st.markdown("**Acción:** Ajusta presupuesto diario según CPA y ROAS objetivo.")

    # 6. Checklist del Proceso
    else:
        st.title("📜 Checklist del Proceso")
        st.checkbox("Búsqueda General por Keywords", key="check1", on_change=goto_search)
        st.checkbox("Analizar creatividades replicadas", key="check2", on_change=goto_deep)
        st.checkbox("Investigar páginas competidoras", key="check3", on_change=goto_comp)
        st.checkbox("Calcular rentabilidad", key="check4", on_change=goto_calc)
        st.checkbox("Revisar checklist final antes de lanzar", key="check5", on_change=goto_check)

if __name__ == "__main__":
    main()
