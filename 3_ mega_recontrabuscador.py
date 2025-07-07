# mega_recontrabuscador.py
# 100% SCRAPING REAL · Facebook Ads Library · Dashboard Profesional
# Requisitos:
# pip install -U streamlit selenium pandas matplotlib deep-translator
# Descarga el ChromeDriver correcto: https://chromedriver.chromium.org/downloads

import os
import time
import re
import random
import pandas as pd
import streamlit as st
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
PAISES_PT  = ["BR","PT"]
PAISES_FR  = ["FR"]
PAISES_DE  = ["DE"]
PAISES_NL  = ["NL"]
PAISES_IT  = ["IT"]
PAISES_CN  = ["CN"]
PAISES_HI  = ["IN"]
PAISES_JA  = ["JP"]
PAISES_KO  = ["KR"]
PAISES_ID  = ["ID"]
PAISES_AR  = ["EG","MA"]
COUNTRY2NAME = {
    "US":"Estados Unidos","CA":"Canadá","MX":"México","GB":"Reino Unido","DE":"Alemania","ES":"España",
    "NL":"Países Bajos","FR":"Francia","CN":"China","IN":"India","JP":"Japón","KR":"Corea del Sur",
    "ID":"Indonesia","BR":"Brasil","PT":"Portugal","AR":"Argentina","CO":"Colombia","CL":"Chile",
    "PE":"Perú","AU":"Australia","NZ":"Nueva Zelanda","ZA":"Sudáfrica","NG":"Nigeria","KE":"Kenia",
    "EG":"Egipto","MA":"Marruecos"
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
    if incognito:
        opts.add_argument("--incognito")
    return Chrome(options=opts)

def traducir_palabras(palabras, idioma_destino):
    traducidas = []
    for p in palabras:
        try:
            traducidas.append(GoogleTranslator(source='auto', target=idioma_destino).translate(p))
        except:
            traducidas.append(p)
        time.sleep(0.5 + random.random()*0.5)
    return traducidas

def count_ads_quick(keyword:str, country:str) -> int:
    driver = get_driver(incognito=True)
    url = (
        f"https://www.facebook.com/ads/library/"
        f"?active_status=all&ad_type=all&country={country}&q={quote(keyword)}"
    )
    driver.get(url)
    try:
        txt = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(text(),' result') or contains(text(),' resultado')]"
            ))
        ).text
        return int(re.sub(r"[^\d]","", txt))
    except:
        return 0
    finally:
        driver.quit()
        time.sleep(0.5 + random.random()*0.5)

def obtener_anuncios(keyword, country, max_cards=10):
    driver = get_driver()
    url = (
        f"https://www.facebook.com/ads/library/"
        f"?active_status=all&ad_type=all&country={country}&q={quote(keyword)}"
    )
    driver.get(url)
    time.sleep(2)
    anuncios = []
    try:
        cards = driver.find_elements(By.CSS_SELECTOR, ".x1lliihq")
        for c in cards[:max_cards]:
            try:
                copy = c.text.strip()
                link = c.find_element(By.TAG_NAME, "a").get_attribute("href")
                if len(copy) < 10:
                    continue
                anuncios.append({
                    "País": country,
                    "Copy": copy[:300] + "…" if len(copy)>300 else copy,
                    "Link": link
                })
            except:
                continue
    except:
        pass
    driver.quit()
    return anuncios

def color_duplicado(n):
    return "red" if n>=5 else "yellow" if n>=3 else "purple"

#───────────────────────────── INTERFAZ ─────────────────────────────#

st.sidebar.title("Selecciona una tarea:")
menu = st.sidebar.radio("", [
    "🚀 Guía de Inicio Rápido",
    "📊 Demanda por País",
    "💡 Inspiración de Keywords",
    "🔎 Búsqueda General por Palabras Clave",
    "🔬 Análisis Profundo de Página de Resultados",
    "🕵️‍♂️ Análisis Específico de Competidores",
    "🧮 Calculadora de Rentabilidad",
    "📋 Checklist del Proceso"
])

# 0. GUÍA RÁPIDA
if menu=="🚀 Guía de Inicio Rápido":
    st.header("🚀 Guía de Inicio Rápido")
    st.markdown(...)

# 1. DEMANDA POR PAÍS
elif menu=="📊 Demanda por País":
    st.header("📊 Demanda por País")
    def clear_paises_demanda():
        st.session_state["paises_demanda"] = []
    idioma = st.selectbox(
        "Idioma base", LANGS,
        key="idioma_demanda",
        on_change=clear_paises_demanda
    )
    palabras = st.text_area("Keywords (coma-separadas)", key="kw_demanda")
    paises = st.multiselect(
        "Países destino", ALL_COUNTRIES,
        default=LANG_DEFAULT.get(idioma, []),
        key="paises_demanda"
    )
    traducir = st.checkbox("Traducir automáticamente", value=True)
    col1, col2 = st.columns(2)

    if col1.button("Medir demanda"):
        ...

    if col2.button("→Enviar a Búsqueda"):
        ...

    st.markdown(...)

# (El resto de menús permanece igual)
#───────────────────────────── FIN DEL SCRIPT ─────────────────────────────#
