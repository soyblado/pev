"🎯 Analizador de Frases Reales": {
            "siguiente": "🔍 Búsqueda de Productos",
            "accion": "Usa las frases encontradas para buscar productos",
            "descripcion": "Aplica las frases reales encontradas para buscar productos específicos"
        },# mega_buscador_pev_simple.py
# HERRAMIENTA SIMPLE Y FUNCIONAL PARA ENCONTRAR PRODUCTOS DIGITALES RENTABLES

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

# ==========================================
# CONFIGURACIÓN INICIAL
# ==========================================

st.set_page_config(
    page_title="Mega Buscador PEV",
    page_icon="💰",
    layout="wide"
)

# ==========================================
# FRASES CLAVE PARA INFOPRODUCTOS
# ==========================================

FRASES_CLAVE = {
    "spanish": [
        "acceso inmediato a",
        "descargar ahora gratis",
        "método comprobado",
        "transforma tu vida",
        "descubre el secreto",
        "guía completa",
        "sistema probado",
        "resultados garantizados"
    ],
    "portuguese": [
        "tenha acesso imediato a",
        "baixar agora gratis",
        "metodo comprovado",
        "transforme sua vida",
        "descubra o segredo",
        "guia completo",
        "sistema comprovado",
        "resultados garantidos"
    ],
    "english": [
        "get instant access to",
        "download now free",
        "proven method",
        "transform your life",
        "discover the secret",
        "complete guide",
        "proven system",
        "guaranteed results"
    ],
    "french": [
        "accès immédiat à",
        "télécharger maintenant gratuitement",
        "méthode prouvée",
        "transformez votre vie",
        "découvrez le secret",
        "guide complet"
    ],
    "german": [
        "sofortiger zugang zu",
        "jetzt kostenlos herunterladen",
        "bewährte methode",
        "verwandeln sie ihr leben",
        "entdecken sie das geheimnis"
    ]
}

# ==========================================
# PAÍSES MÁS RENTABLES
# ==========================================

PAISES_RENTABLES = {
    "alta_rentabilidad": ["US", "CA", "GB", "DE", "NL", "FR", "AU", "NZ", "BR"],
    "buena_rentabilidad": ["JP", "KR", "CN", "ZA"],
    "rentabilidad_media": ["MX", "ES", "AR", "CO", "CL", "PE", "IN", "ID"]
}

# ==========================================
# CONFIGURACIONES
# ==========================================

LANGS = {
    "Español": "spanish",
    "Portugués": "portuguese", 
    "Inglés": "english",
    "Francés": "french",
    "Alemán": "german"
}

LANG2ISO = {
    "spanish": "es",
    "portuguese": "pt",
    "english": "en", 
    "french": "fr",
    "german": "de"
}

COUNTRY2NAME = {
    "US": "Estados Unidos", "CA": "Canadá", "MX": "México", "GB": "Reino Unido",
    "DE": "Alemania", "ES": "España", "NL": "Países Bajos", "FR": "Francia",
    "CN": "China", "IN": "India", "JP": "Japón", "KR": "Corea del Sur",
    "ID": "Indonesia", "BR": "Brasil", "AR": "Argentina", "CO": "Colombia",
    "CL": "Chile", "PE": "Perú", "AU": "Australia", "NZ": "Nueva Zelanda",
    "ZA": "Sudáfrica"
}

ALL_COUNTRIES = list(COUNTRY2NAME.keys())

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# ==========================================
# FUNCIONES PRINCIPALES
# ==========================================

def get_driver():
    """Driver optimizado para scraping con anti-detección"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-images")
    
    # ANTI-BAN: User agents rotativos y más realistas
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    options.add_argument(f"--user-agent={random.choice(user_agents)}")
    
    # ANTI-BAN: Headers adicionales para parecer más humano
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # ANTI-BAN: Configuraciones adicionales
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    
    driver = webdriver.Chrome(options=options)
    
    # ANTI-BAN: Eliminar propiedades que detectan automation
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def evaluar_facilidad_copia(descripcion):
    """Evalúa qué tan fácil es copiar el producto"""
    texto = descripcion.lower()
    
    # Productos fáciles de copiar
    faciles = ["ebook", "pdf", "guía", "guide", "manual", "prompts", "plantilla", "template"]
    
    # Productos difíciles de copiar
    dificiles = ["aplicación", "application", "plataforma", "platform", "software", "app", "saas"]
    
    # Productos medios
    medios = ["curso", "course", "video", "training", "masterclass", "webinar"]
    
    if any(palabra in texto for palabra in dificiles):
        return {
            "dificultad": "DIFÍCIL",
            "recomendacion": "❌ EVITAR - Muy complejo",
            "color": "🔴"
        }
    elif any(palabra in texto for palabra in faciles):
        return {
            "dificultad": "FÁCIL", 
            "recomendacion": "✅ COPIAR - Perfecto",
            "color": "🟢"
        }
    elif any(palabra in texto for palabra in medios):
        return {
            "dificultad": "MEDIO",
            "recomendacion": "⚠️ EVALUAR", 
            "color": "🟡"
        }
    else:
        return {
            "dificultad": "DESCONOCIDO",
            "recomendacion": "❓ INVESTIGAR",
            "color": "⚪"
        }

def analizar_rentabilidad(total_anuncios):
    """Analiza potencial de rentabilidad"""
    
    if total_anuncios >= 100:
        return {
            "estado": "🔥 SÚPER RENTABLE",
            "accion": "COPIAR INMEDIATAMENTE",
            "prioridad": 1
        }
    elif total_anuncios >= 50:
        return {
            "estado": "💰 MUY RENTABLE",
            "accion": "COPIAR HOY",
            "prioridad": 2
        }
    elif total_anuncios >= 30:
        return {
            "estado": "✅ RENTABLE",
            "accion": "COPIAR EN 24H",
            "prioridad": 3
        }
    elif total_anuncios >= 10:
        return {
            "estado": "⚠️ POSIBLE",
            "accion": "INVESTIGAR MÁS",
            "prioridad": 4
        }
    else:
        return {
            "estado": "❌ BAJA RENTABILIDAD",
            "accion": "BUSCAR OTROS",
            "prioridad": 5
        }

def traducir_palabras(palabras, idioma_destino):
    """Traducir keywords"""
    if idioma_destino == "spanish":
        return palabras
    
    iso_code = LANG2ISO.get(idioma_destino, "en")
    translator = GoogleTranslator(source="es", target=iso_code)
    
    traducidas = []
    for palabra in palabras:
        try:
            traducida = translator.translate(palabra)
            traducidas.append(traducida)
            time.sleep(0.5)
        except Exception as e:
            st.warning(f"Error traduciendo '{palabra}': {e}")
            traducidas.append(palabra)
    
    return traducidas

def contar_anuncios(keyword, country):
    """Contar anuncios en Facebook Ads Library"""
    driver = get_driver()
    try:
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered&media_type=all"
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        
        try:
            result_element = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'result')]"))
            )
            result_text = result_element.text
            
            numbers = re.findall(r'\d{1,3}(?:,\d{3})*', result_text)
            if numbers:
                count = int(numbers[0].replace(',', ''))
                return count
            else:
                return 0
                
        except TimeoutException:
            return 0
            
    except Exception as e:
        st.error(f"Error contando anuncios: {e}")
        return 0
    finally:
        driver.quit()
        time.sleep(0.5)

def analizar_frases_reales(keyword, country, max_anuncios=30):
    """Analiza anuncios reales para extraer frases comunes que contengan la keyword"""
    driver = get_driver()
    frases_encontradas = []
    
    try:
        # Buscar la keyword en Facebook Ads Library
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered&media_type=all"
        driver.get(url)
        
        # ANTI-BAN: Esperas más largas y comportamiento humano
        time.sleep(random.uniform(3, 5))
        
        # Scroll gradual para simular comportamiento humano
        for i in range(3):  # Reducido de 5 a 3 para menos carga
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            time.sleep(random.uniform(2, 4))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(2, 4))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3, 5))
        
        cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='ad-copy']")
        
        texts = []
        for card in cards[:max_anuncios]:  # Limitado para no sobrecargar
            try:
                text = card.text.lower().strip()
                if len(text) > 20 and keyword.lower() in text:
                    texts.append(text)
                # ANTI-BAN: Pausa entre extracciones
                time.sleep(random.uniform(0.5, 1))
            except:
                continue
        
        # Extraer frases que contengan la keyword
        import re
        
        patterns = [
            # Patrones comunes de marketing
            rf"[^.!?]*{re.escape(keyword.lower())}[^.!?]*",  # Frases completas con la keyword
            rf"\b\w+\s+{re.escape(keyword.lower())}\s+\w+\b",  # Palabras antes y después
            rf"{re.escape(keyword.lower())}\s+en\s+\d+\s+días?",  # "keyword en X días"
            rf"cómo\s+[^.!?]*{re.escape(keyword.lower())}[^.!?]*",  # "cómo ... keyword"
            rf"método\s+[^.!?]*{re.escape(keyword.lower())}[^.!?]*",  # "método ... keyword"
            rf"guía\s+[^.!?]*{re.escape(keyword.lower())}[^.!?]*",  # "guía ... keyword"
            rf"supera?\s+[^.!?]*{re.escape(keyword.lower())}[^.!?]*",  # "superar ... keyword"
        ]
        
        frase_counts = {}
        
        for text in texts:
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Limpiar y normalizar la frase
                    frase = re.sub(r'\s+', ' ', match.strip())
                    if 10 <= len(frase) <= 80:  # Frases de longitud razonable
                        frase_counts[frase] = frase_counts.get(frase, 0) + 1
        
        # Ordenar por frecuencia y tomar las mejores
        frases_ordenadas = sorted(frase_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Filtrar frases que aparecen al menos 2 veces
        frases_encontradas = [
            {"frase": frase, "frecuencia": freq} 
            for frase, freq in frases_ordenadas[:15] 
            if freq >= 2
        ]
        
    except Exception as e:
        st.error(f"Error analizando frases reales: {e}")
    finally:
        driver.quit()
        # ANTI-BAN: Pausa antes de siguiente análisis
        time.sleep(random.uniform(2, 4))
    
    return frases_encontradas
    """Obtener anuncios detallados"""
    driver = get_driver()
    anuncios = []
    
    try:
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered&media_type=all"
        driver.get(url)
        
        time.sleep(3)
        
        # Scroll para cargar contenido
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='ad-card']")
        
        for card in cards[:max_anuncios]:
            try:
                copy_element = card.find_element(By.CSS_SELECTOR, "[data-testid='ad-copy']")
                copy_text = copy_element.text
                
                if len(copy_text) > 20:
                    # Evaluar facilidad de copia
                    facilidad = evaluar_facilidad_copia(copy_text)
                    
                    # Buscar enlace
                    try:
                        link_element = card.find_element(By.CSS_SELECTOR, "a[href]")
                        link = link_element.get_attribute("href")
                    except:
                        link = "No disponible"
                    
                    anuncios.append({
                        "Copy": copy_text[:200] + "..." if len(copy_text) > 200 else copy_text,
                        "Link": link,
                        "Dificultad": facilidad["dificultad"],
                        "Recomendación": facilidad["recomendacion"],
                        "Color": facilidad["color"]
                    })
                    
            except Exception as e:
                continue
                
    except Exception as e:
        st.error(f"Error obteniendo anuncios: {e}")
    finally:
        driver.quit()
        time.sleep(0.5)
    
    return anuncios

# ==========================================
# INTERFAZ STREAMLIT
# ==========================================

st.title("💰 Mega Buscador PEV")
st.markdown("### *Encuentra Productos Digitales Rentables para Copiar*")

# ==========================================
# INICIALIZACIÓN DE SESSION STATE
# ==========================================

# Inicializar variables de sesión para persistencia
if 'analisis_demanda_resultados' not in st.session_state:
    st.session_state.analisis_demanda_resultados = None

if 'productos_encontrados' not in st.session_state:
    st.session_state.productos_encontrados = []

if 'competidores_analizados' not in st.session_state:
    st.session_state.competidores_analizados = []

if 'paises_alta_demanda' not in st.session_state:
    st.session_state.paises_alta_demanda = []

if 'keywords_exitosas' not in st.session_state:
    st.session_state.keywords_exitosas = []

# ==========================================
# FUNCIÓN DE NAVEGACIÓN
# ==========================================

def mostrar_siguiente_paso(menu_actual):
    """Muestra sugerencia del siguiente paso en el proceso"""
    pasos_proceso = {
        "🚀 Inicio Rápido": {
            "siguiente": "📊 Análisis de Demanda",
            "accion": "Analiza la demanda en países rentables",
            "descripcion": "Encuentra los países y keywords con más oportunidades"
        },
        "📊 Análisis de Demanda": {
            "siguiente": "🔍 Búsqueda de Productos",
            "accion": "Busca productos específicos para copiar",
            "descripcion": "Encuentra productos detallados en los países con alta demanda"
        },
        "🔍 Búsqueda de Productos": {
            "siguiente": "🕵️ Espionaje de Competidores",
            "accion": "Analiza a tu competencia",
            "descripcion": "Valida el mercado analizando competidores específicos"
        },
        "🕵️ Espionaje de Competidores": {
            "siguiente": "🧮 Calculadora de Ganancias",
            "accion": "Calcula las ganancias proyectadas",
            "descripcion": "Estima cuánto puedes ganar con los productos encontrados"
        },
        "🧮 Calculadora de Ganancias": {
            "siguiente": "🔍 Búsqueda de Productos",
            "accion": "Busca más productos o refina tu búsqueda",
            "descripcion": "Continúa encontrando más oportunidades rentables"
        }
    }
    
    if menu_actual in pasos_proceso:
        info_siguiente = pasos_proceso[menu_actual]
        
        st.markdown("---")
        st.markdown("### 🚀 Siguiente Paso Recomendado")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(f"**{info_siguiente['siguiente']}**: {info_siguiente['descripcion']}")
        
        with col2:
            if st.button(f"Ir a {info_siguiente['siguiente']}", key=f"next_step_{menu_actual}"):
                st.session_state.menu_seleccionado = info_siguiente['siguiente']
                st.rerun()

# ==========================================
# FUNCIÓN PARA MOSTRAR DATOS PERSISTIDOS
# ==========================================

def mostrar_datos_previos():
    """Muestra resumen de datos de sesiones anteriores"""
    tiene_datos = (
        st.session_state.analisis_demanda_resultados is not None or
        len(st.session_state.productos_encontrados) > 0 or
        len(st.session_state.competidores_analizados) > 0
    )
    
    if tiene_datos:
        with st.sidebar.expander("📊 Datos de Sesión Anterior", expanded=False):
            if st.session_state.analisis_demanda_resultados is not None:
                st.write(f"✅ Análisis de demanda: {len(st.session_state.analisis_demanda_resultados)} resultados")
            
            if len(st.session_state.productos_encontrados) > 0:
                st.write(f"✅ Productos encontrados: {len(st.session_state.productos_encontrados)}")
            
            if len(st.session_state.competidores_analizados) > 0:
                st.write(f"✅ Competidores analizados: {len(st.session_state.competidores_analizados)}")
            
            if len(st.session_state.paises_alta_demanda) > 0:
                st.write(f"✅ Países con alta demanda: {', '.join(st.session_state.paises_alta_demanda[:3])}")

# Menú principal en sidebar
mostrar_datos_previos()

# Usar session state para mantener selección de menú
if 'menu_seleccionado' not in st.session_state:
    st.session_state.menu_seleccionado = "🚀 Inicio Rápido"

menu = st.sidebar.radio(
    "Selecciona una opción:",
    [
        "🚀 Inicio Rápido",
        "📊 Análisis de Demanda",
        "🔍 Búsqueda de Productos", 
        "🕵️ Espionaje de Competidores",
        "🧮 Calculadora de Ganancias"
    ],
    index=[
        "🚀 Inicio Rápido",
        "📊 Análisis de Demanda",
        "🔍 Búsqueda de Productos", 
        "🕵️ Espionaje de Competidores",
        "🧮 Calculadora de Ganancias"
    ].index(st.session_state.menu_seleccionado) if st.session_state.menu_seleccionado in [
        "🚀 Inicio Rápido",
        "📊 Análisis de Demanda",
        "🔍 Búsqueda de Productos", 
        "🕵️ Espionaje de Competidores",
        "🧮 Calculadora de Ganancias"
    ] else 0
)

# Actualizar session state cuando cambie el menú
if menu != st.session_state.menu_seleccionado:
    st.session_state.menu_seleccionado = menu

# ==========================================
# MÓDULO 1: INICIO RÁPIDO
# ==========================================

if menu == "🚀 Inicio Rápido":
    st.header("🚀 Cómo Generar Dinero Rápidamente")
    
    st.markdown("""
    ## 💰 **Proceso Para Ganar Dinero**
    
    ### **Paso 1: Encuentra Productos Exitosos**
    - 🎯 Enfócate en países rentables (US, BR, GB, DE)
    - 🔍 Busca productos con 30+ anuncios activos
    - 📱 Prioriza productos digitales simples
    
    ### **Paso 2: Evalúa Facilidad para Copiar**
    - 🟢 **FÁCIL**: E-books, PDFs, guías → COPIAR
    - 🟡 **MEDIO**: Cursos, videos → EVALUAR
    - 🔴 **DIFÍCIL**: Apps, software → EVITAR
    
    ### **Paso 3: Modela y Mejora**
    - 📝 Copia la estructura de ventas
    - 🎨 Mejora el diseño original
    - 💡 Añade tu toque personal
    
    ### **Paso 4: Monetiza Rápido**
    - 🚀 Sube a plataformas (Hotmart, ClickBank)
    - 💰 Precio similar al original
    - 📈 Reinvierte ganancias
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("💡 **Países Más Rentables**")
        for pais in PAISES_RENTABLES["alta_rentabilidad"]:
            st.markdown(f"- {COUNTRY2NAME[pais]}")
    
    with col2:
        st.info("🎯 **Tipos de Productos Ideales**")
        st.markdown("""
        - 📚 E-books y guías PDF
        - 📋 Plantillas y checklists
        - 🎯 Prompts para IA
        - 📝 Manuales paso a paso
        """)

# ==========================================
# MÓDULO 2: ANÁLISIS DE DEMANDA
# ==========================================

elif menu == "📊 Análisis de Demanda":
    st.header("📊 Análisis de Demanda por Países")
    
    col1, col2 = st.columns(2)
    
    with col1:
        idioma_base = st.selectbox("Idioma base:", list(LANGS.keys()))
        keywords_input = st.text_area("Keywords (separadas por comas):", "ebook, curso, guía")
    
    with col2:
        st.markdown("**Selección de países:**")
        
        incluir_alta = st.checkbox("🔥 Países alta rentabilidad", value=True)
        incluir_buena = st.checkbox("⭐ Países buena rentabilidad", value=True)
        incluir_media = st.checkbox("📝 Países rentabilidad media", value=False)
        
        paises_selected = []
        if incluir_alta:
            paises_selected.extend(PAISES_RENTABLES["alta_rentabilidad"])
        if incluir_buena:
            paises_selected.extend(PAISES_RENTABLES["buena_rentabilidad"])
        if incluir_media:
            paises_selected.extend(PAISES_RENTABLES["rentabilidad_media"])
    
    traducir_auto = st.checkbox("Traducir automáticamente", value=True)
    
    if st.button("📊 Analizar Demanda", type="primary"):
        if keywords_input and paises_selected:
            keywords = [kw.strip() for kw in keywords_input.split(",")]
            
            with st.spinner("Analizando demanda..."):
                resultados = []
                
                for pais in paises_selected:
                    if traducir_auto:
                        # Mapeo de idiomas por país
                        pais_lang_map = {
                            "BR": "portuguese",
                            "US": "english", "CA": "english", "GB": "english", 
                            "AU": "english", "NZ": "english", "ZA": "english",
                            "FR": "french",
                            "DE": "german", "NL": "german"
                        }
                        idioma_pais = pais_lang_map.get(pais, "spanish")
                        keywords_traducidas = traducir_palabras(keywords, idioma_pais)
                    else:
                        keywords_traducidas = keywords
                    
                    for keyword in keywords_traducidas:
                        count = contar_anuncios(keyword, pais)
                        rentabilidad = analizar_rentabilidad(count)
                        
                        resultados.append({
                            "País": f"{COUNTRY2NAME[pais]} ({pais})",
                            "Keyword": keyword,
                            "Anuncios": count,
                            "Estado": rentabilidad["estado"],
                            "Acción": rentabilidad["accion"]
                        })
            
            if resultados:
                # Guardar resultados en session state
                st.session_state.analisis_demanda_resultados = resultados
                
                # Identificar países con alta demanda para siguiente módulo
                paises_alta_demanda = [
                    r["País"].split("(")[1].replace(")", "") 
                    for r in resultados if r["Anuncios"] >= 50
                ]
                st.session_state.paises_alta_demanda = paises_alta_demanda
                
                # Keywords exitosas
                keywords_exitosas = [
                    r["Keyword"] for r in resultados if r["Anuncios"] >= 30
                ]
                st.session_state.keywords_exitosas = list(set(keywords_exitosas))
                
                df = pd.DataFrame(resultados)
                df = df.sort_values("Anuncios", ascending=False)
                
                st.markdown(f"### 📊 Resultados: {len(df)} combinaciones analizadas")
                st.dataframe(df, use_container_width=True)
                
                # Resumen
                alta_demanda = len(df[df["Anuncios"] >= 50])
                demanda_media = len(df[(df["Anuncios"] >= 30) & (df["Anuncios"] < 50)])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🔥 Alta Demanda", alta_demanda)
                with col2:
                    st.metric("✅ Demanda Media", demanda_media)
                with col3:
                    total_anuncios = df["Anuncios"].sum()
                    st.metric("📊 Total Anuncios", f"{total_anuncios:,}")
                
                if alta_demanda >= 3:
                    st.success("🔥 EXCELENTE: Múltiples oportunidades de alta demanda")
                elif alta_demanda >= 1:
                    st.info("✅ BUENO: Algunas oportunidades de alta demanda")
                else:
                    st.warning("⚠️ Considera cambiar keywords o ampliar países")
                
                # Mostrar siguiente paso
                mostrar_siguiente_paso("📊 Análisis de Demanda")
            else:
                st.error("No se obtuvieron resultados")
        else:
            st.error("Completa todos los campos")

# ==========================================
# MÓDULO 3: BÚSQUEDA DE PRODUCTOS
# ==========================================

elif menu == "🔍 Búsqueda de Productos":
    st.header("🔍 Búsqueda de Productos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        idioma_busqueda = st.selectbox("Idioma:", list(LANGS.keys()))
        
        # Pre-cargar países de alta demanda si están disponibles
        default_countries = [p for p in (st.session_state.paises_alta_demanda if st.session_state.paises_alta_demanda else ["US", "BR", "GB"]) if p in ALL_COUNTRIES]
        paises_busqueda = st.multiselect(
            "Países objetivo:",
            ALL_COUNTRIES,
            default=default_countries,
            format_func=lambda x: COUNTRY2NAME[x],
            help="Países pre-cargados del análisis de demanda anterior" if st.session_state.paises_alta_demanda else None
        )
    
    with col2:
        # Pre-cargar frases seleccionadas del analizador si están disponibles
        if 'frases_seleccionadas' in st.session_state and st.session_state.frases_seleccionadas:
            usar_frases_analizadas = st.checkbox("Usar frases analizadas", value=True)
            
            if usar_frases_analizadas:
                st.markdown("**Frases del analizador:**")
                frases_para_usar = st.multiselect(
                    "Selecciona frases:",
                    st.session_state.frases_seleccionadas,
                    default=st.session_state.frases_seleccionadas[:3],
                    help="Frases reales encontradas en el analizador"
                )
                keywords_text = ", ".join(frases_para_usar)
            else:
                keywords_text = st.text_area("Keywords personalizadas:", "ebook, guía")
        else:
            keywords_text = st.text_area("Keywords personalizadas:", "ebook, guía")
            st.info("💡 Tip: Usa el 'Analizador de Frases Reales' para encontrar frases que realmente funcionan")
    
    col1, col2 = st.columns(2)
    with col1:
        min_anuncios = st.number_input("Mínimo anuncios:", min_value=1, value=30)
        traducir_auto = st.checkbox("Traducir automáticamente", value=True)
    with col2:
        solo_faciles = st.checkbox("Solo productos fáciles de copiar", value=True)
    
    if st.button("🔍 Buscar Productos", type="primary"):
        if keywords_text and paises_busqueda:
            keywords = [kw.strip() for kw in keywords_text.split(",")]
            
            with st.spinner("Analizando demanda y buscando productos..."):
                todos_productos = []
                resultados_conteo = []
                
                for pais in paises_busqueda:
                    st.write(f"🔍 Analizando {COUNTRY2NAME[pais]}...")
                    
                    # Traducir keywords al idioma específico del país
                    if traducir_auto:
                        pais_lang_map = {
                            "BR": "portuguese",
                            "US": "english", "CA": "english", "GB": "english", 
                            "AU": "english", "NZ": "english", "ZA": "english",
                            "FR": "french",
                            "DE": "german", "NL": "german"
                        }
                        idioma_pais = pais_lang_map.get(pais, "spanish")
                        keywords_pais = traducir_palabras(keywords, idioma_pais)
                    else:
                        keywords_pais = keywords
                    
                    for keyword in keywords_pais:
                        # PASO 1: Contar anuncios primero
                        count = contar_anuncios(keyword, pais)
                        rentabilidad = analizar_rentabilidad(count)
                        
                        resultados_conteo.append({
                            "País": COUNTRY2NAME[pais],
                            "Keyword": keyword,
                            "Anuncios": count,
                            "Estado": rentabilidad["estado"]
                        })
                        
                        # PASO 2: Solo buscar productos detallados si tiene 30+ anuncios
                        if count >= min_anuncios:
                            st.write(f"  ✅ {keyword} ({count} anuncios) - Buscando productos...")
                            productos = obtener_anuncios(keyword, pais, max_anuncios=15)
                            
                            for producto in productos:
                                producto["País"] = f"{COUNTRY2NAME[pais]} ({pais})"
                                producto["Keyword"] = keyword
                                producto["Total_Anuncios"] = count
                                producto["Estado_Demanda"] = rentabilidad["estado"]
                                todos_productos.append(producto)
                        else:
                            st.write(f"  ❌ {keyword} ({count} anuncios) - Muy pocos anuncios, saltando...")
                
                # Mostrar resumen de conteo
                if resultados_conteo:
                    st.markdown("### 📊 Análisis de Demanda por Keyword")
                    df_conteo = pd.DataFrame(resultados_conteo)
                    df_conteo = df_conteo.sort_values("Anuncios", ascending=False)
                    st.dataframe(df_conteo, use_container_width=True)
                    
                    # Métricas de filtrado
                    keywords_exitosas = len(df_conteo[df_conteo["Anuncios"] >= min_anuncios])
                    keywords_totales = len(df_conteo)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Keywords Analizadas", keywords_totales)
                    with col2:
                        st.metric(f"Con {min_anuncios}+ Anuncios", keywords_exitosas)
                    with col3:
                        porcentaje_exito = (keywords_exitosas / keywords_totales * 100) if keywords_totales > 0 else 0
                        st.metric("% Éxito", f"{porcentaje_exito:.1f}%")
                
                if todos_productos:
                    # Guardar productos en session state
                    st.session_state.productos_encontrados = todos_productos
                    
                    df_productos = pd.DataFrame(todos_productos)
                    
                    # Aplicar filtros adicionales
                    if solo_faciles:
                        df_filtrado = df_productos[df_productos["Dificultad"] == "FÁCIL"]
                    else:
                        df_filtrado = df_productos[df_productos["Dificultad"].isin(["FÁCIL", "MEDIO"])]
                    
                    st.markdown(f"### 💰 {len(df_filtrado)} productos encontrados (con {min_anuncios}+ anuncios)")
                    
                    # Mostrar productos con información de demanda
                    for _, producto in df_filtrado.iterrows():
                        with st.container():
                            col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
                            
                            with col1:
                                st.markdown(f"**{producto['Color']} {producto['Dificultad']}**")
                                st.markdown(f"📊 **{producto['Total_Anuncios']} anuncios**")
                            
                            with col2:
                                st.markdown(f"**Copy:** {producto['Copy']}")
                                st.markdown(f"**País:** {producto['País']} | **Keyword:** {producto['Keyword']}")
                                st.markdown(f"**{producto['Recomendación']}**")
                                st.markdown(f"**Demanda:** {producto['Estado_Demanda']}")
                            
                            with col3:
                                st.markdown("**Acción Sugerida**")
                                if "COPIAR" in producto['Recomendación']:
                                    st.success("Copiar")
                                elif "EVALUAR" in producto['Recomendación']:
                                    st.warning("Evaluar")
                                else:
                                    st.info("Revisar")
                            
                            with col4:
                                if producto['Link'] != "No disponible":
                                    st.link_button("🔗 Ver", producto['Link'])
                        
                        st.markdown("---")
                    
                    # Resumen mejorado
                    facilidad_counts = df_filtrado["Dificultad"].value_counts()
                    st.markdown("### 📊 Resumen de Productos Encontrados")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        faciles = facilidad_counts.get("FÁCIL", 0)
                        st.metric("🟢 Fáciles", faciles)
                    with col2:
                        medios = facilidad_counts.get("MEDIO", 0)
                        st.metric("🟡 Medios", medios)
                    with col3:
                        st.metric("📊 Total Productos", len(df_filtrado))
                    with col4:
                        anuncios_promedio = df_filtrado["Total_Anuncios"].mean() if len(df_filtrado) > 0 else 0
                        st.metric("📈 Promedio Anuncios", f"{anuncios_promedio:.0f}")
                    
                    if faciles >= 5:
                        st.success("🔥 EXCELENTE: Múltiples productos fáciles de copiar con alta demanda")
                    elif faciles >= 2:
                        st.info("✅ BUENO: Algunas buenas oportunidades encontradas")
                    else:
                        st.warning("⚠️ POCAS OPCIONES: Considera ajustar filtros o probar otras keywords")
                    
                    # Mostrar siguiente paso
                    mostrar_siguiente_paso("🔍 Búsqueda de Productos")
                
                else:
                    st.warning(f"❌ No se encontraron productos con {min_anuncios}+ anuncios. Intenta:")
                    st.markdown("""
                    - Reducir el mínimo de anuncios requeridos
                    - Probar keywords diferentes
                    - Ampliar la lista de países
                    - Usar frases clave más generales
                    """)
        else:
            st.error("Completa todos los campos")

# ==========================================
# MÓDULO 4: ANALIZADOR DE FRASES REALES
# ==========================================

elif menu == "🎯 Analizador de Frases Reales":
    st.header("🎯 Analizador de Frases Reales")
    
    st.markdown("""
    **Analiza anuncios reales para encontrar frases exitosas que contengan tu keyword**
    
    Ingresa una palabra clave y el sistema analizará anuncios reales para encontrar:
    - Frases comunes que usan esa palabra
    - Patrones de marketing que funcionan
    - Copy real de productos exitosos
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        keyword_analisis = st.text_input("Palabra clave para analizar:", "depresión")
        pais_analisis = st.selectbox(
            "País para analizar:",
            ALL_COUNTRIES,
            index=0,
            format_func=lambda x: COUNTRY2NAME[x]
        )
    
    with col2:
        max_anuncios_analisis = st.number_input("Máximo anuncios a analizar:", min_value=10, max_value=50, value=30)
        st.caption("⚠️ Máximo 50 para evitar bloqueos")
        min_frecuencia = st.number_input("Mínima frecuencia de frase:", min_value=1, value=2)
    
    if st.button("🔍 Analizar Frases Reales", type="primary"):
        if keyword_analisis.strip():
            with st.spinner(f"Analizando anuncios reales con '{keyword_analisis}' en {COUNTRY2NAME[pais_analisis]}..."):
                frases_reales = analizar_frases_reales(keyword_analisis, pais_analisis, max_anuncios_analisis)
                
                if frases_reales:
                    st.markdown(f"### 🎯 Frases Reales Encontradas para '{keyword_analisis}'")
                    st.markdown(f"*Analizados en {COUNTRY2NAME[pais_analisis]} - Mínimo {min_frecuencia} apariciones*")
                    
                    # Filtrar por frecuencia mínima
                    frases_filtradas = [f for f in frases_reales if f["frecuencia"] >= min_frecuencia]
                    
                    if frases_filtradas:
                        # Mostrar frases encontradas
                        st.markdown("#### 📝 Frases que puedes usar:")
                        
                        for i, frase_data in enumerate(frases_filtradas, 1):
                            frase = frase_data["frase"]
                            freq = frase_data["frecuencia"]
                            
                            # Determinar color según frecuencia
                            if freq >= 5:
                                color = "🔥"
                                status = "MUY COMÚN"
                            elif freq >= 3:
                                color = "⭐"
                                status = "COMÚN"
                            else:
                                color = "📝"
                                status = "OCASIONAL"
                            
                            with st.container():
                                col1, col2, col3 = st.columns([4, 1, 1])
                                
                                with col1:
                                    st.markdown(f"**{i}. {frase}**")
                                
                                with col2:
                                    st.markdown(f"{color} **{freq}x**")
                                
                                with col3:
                                    if st.button("✅ Usar", key=f"usar_frase_{i}"):
                                        # Agregar a session state para usar en búsquedas
                                        if 'frases_seleccionadas' not in st.session_state:
                                            st.session_state.frases_seleccionadas = []
                                        
                                        if frase not in st.session_state.frases_seleccionadas:
                                            st.session_state.frases_seleccionadas.append(frase)
                                            st.success(f"Frase agregada: {frase}")
                                        else:
                                            st.info("Ya está seleccionada")
                        
                            # Resumen de frases seleccionadas
                            if 'frases_seleccionadas' in st.session_state and st.session_state.frases_seleccionadas:
                                st.markdown("---")
                                st.markdown("### ✅ Frases Seleccionadas")
                                
                                for frase in st.session_state.frases_seleccionadas:
                                    col1, col2 = st.columns([4, 1])
                                    with col1:
                                        st.markdown(f"- {frase}")
                                    with col2:
                                        if st.button("❌", key=f"remove_{frase[:20]}"):
                                            st.session_state.frases_seleccionadas.remove(frase)
                                            st.rerun()
                                
                                # Mostrar información sobre usar las frases
                                st.info("💡 Estas frases se cargarán automáticamente en 'Búsqueda de Productos'")
                    
                    else:
                        st.warning(f"No se encontraron frases con frecuencia mínima de {min_frecuencia}")
                        st.markdown("**Intenta:**")
                        st.markdown("- Reducir la frecuencia mínima")
                        st.markdown("- Probar en otro país")
                        st.markdown("- Usar una keyword más general")
                
                    # Estadísticas del análisis
                    st.markdown("### 📊 Estadísticas del Análisis")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Frases Encontradas", len(frases_filtradas))
                    with col2:
                        avg_freq = sum(f["frecuencia"] for f in frases_filtradas) / len(frases_filtradas)
                        st.metric("Frecuencia Promedio", f"{avg_freq:.1f}")
                    with col3:
                        max_freq = max(f["frecuencia"] for f in frases_filtradas)
                        st.metric("Máxima Frecuencia", max_freq)
                    
                    # Mostrar siguiente paso
                    mostrar_siguiente_paso("🎯 Analizador de Frases Reales")
                
                else:
                    st.error(f"No se encontraron frases para '{keyword_analisis}' en {COUNTRY2NAME[pais_analisis]}")
                    st.markdown("**Posibles causas:**")
                    st.markdown("- La keyword no tiene suficientes anuncios")
                    st.markdown("- Prueba con una palabra más común")
                    st.markdown("- Intenta en otro país con más actividad publicitaria")
        
        else:
            st.error("Por favor, ingresa una keyword para analizar")

# ==========================================
# MÓDULO 5: ESPIONAJE DE COMPETIDORES
# ==========================================

elif menu == "🕵️ Espionaje de Competidores":
    st.header("🕵️ Análisis de Competidores")
    
    competidores_input = st.text_area(
        "Lista de dominios competidores (uno por línea):",
        "ejemplo.com\ncompetidor2.com"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        pais_analisis = st.selectbox("País análisis:", ALL_COUNTRIES, index=0, format_func=lambda x: COUNTRY2NAME[x])
    with col2:
        min_anuncios_comp = st.number_input("Mínimo anuncios competencia:", min_value=1, value=10)
    
    if st.button("🕵️ Analizar Competidores", type="primary"):
        if competidores_input.strip():
            competidores = [comp.strip() for comp in competidores_input.split("\n") if comp.strip()]
            
            with st.spinner("Analizando competidores..."):
                resultados_comp = []
                
                for competidor in competidores:
                    count = contar_anuncios(competidor, pais_analisis)
                    rentabilidad = analizar_rentabilidad(count)
                    
                    if count >= min_anuncios_comp:
                        resultados_comp.append({
                            "Competidor": competidor,
                            "Anuncios": count,
                            "Estado": rentabilidad["estado"],
                            "Acción": rentabilidad["accion"],
                            "URL": f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={pais_analisis}&q={competidor}"
                        })
                
                if resultados_comp:
                    # Guardar resultados en session state
                    st.session_state.competidores_analizados = resultados_comp
                    
                    # Ordenar por anuncios
                    resultados_comp.sort(key=lambda x: x["Anuncios"], reverse=True)
                    
                    st.markdown("### 📊 Resultados del Análisis")
                    
                    for resultado in resultados_comp:
                        with st.container():
                            col1, col2, col3, col4 = st.columns([2, 1, 2, 1])
                            
                            with col1:
                                st.markdown(f"**🌐 {resultado['Competidor']}**")
                            
                            with col2:
                                st.metric("Anuncios", resultado["Anuncios"])
                            
                            with col3:
                                if resultado["Anuncios"] >= 50:
                                    st.success(resultado["Estado"])
                                elif resultado["Anuncios"] >= 30:
                                    st.info(resultado["Estado"])
                                else:
                                    st.warning(resultado["Estado"])
                                st.markdown(f"**{resultado['Acción']}**")
                            
                            with col4:
                                st.link_button("🔗 Ver Ads", resultado["URL"])
                            
                            st.markdown("---")
                    
                    # Resumen
                    total_anuncios = sum([r["Anuncios"] for r in resultados_comp])
                    competidores_activos = len(resultados_comp)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Anuncios", f"{total_anuncios:,}")
                    with col2:
                        st.metric("Competidores Activos", competidores_activos)
                    
                    if competidores_activos >= 3:
                        st.success("✅ Mercado validado - Múltiples competidores activos")
                    elif competidores_activos >= 1:
                        st.info("⚠️ Mercado moderado - Algunos competidores")
                    else:
                        st.warning("❌ Mercado poco activo")
                    
                    # Mostrar siguiente paso
                    mostrar_siguiente_paso("🕵️ Espionaje de Competidores")
                
                else:
                    st.warning("No se encontraron competidores con suficiente actividad publicitaria")
        else:
            st.error("Ingresa al menos un competidor")

# ==========================================
# MÓDULO 6: CALCULADORA DE GANANCIAS
# ==========================================

elif menu == "🧮 Calculadora de Ganancias":
    st.header("🧮 Calculadora de Ganancias Proyectadas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Parámetros del Producto")
        precio_venta = st.number_input("Precio de venta ($):", min_value=1.0, value=47.0, step=1.0)
        cpa_estimado = st.number_input("CPA estimado ($):", min_value=0.1, value=15.0, step=0.1)
        conversion_rate = st.number_input("Tasa de conversión (%):", min_value=0.1, value=2.0, step=0.1)
        comision_plataforma = st.number_input("Comisión plataforma (%):", min_value=0.0, value=7.0, step=0.5)
    
    with col2:
        st.markdown("### 📊 Proyecciones")
        visitantes_diarios = st.number_input("Visitantes por día:", min_value=1, value=1000, step=100)
        dias_proyeccion = st.number_input("Días proyección:", min_value=1, value=30, step=1)
        
        # Cálculos automáticos
        ventas_diarias = int(visitantes_diarios * (conversion_rate / 100))
        revenue_bruto_diario = ventas_diarias * precio_venta
        costo_ads_diario = visitantes_diarios * (cpa_estimado / (conversion_rate / 100)) if conversion_rate > 0 else 0
        comision_diaria = revenue_bruto_diario * (comision_plataforma / 100)
        ganancia_neta_diaria = revenue_bruto_diario - costo_ads_diario - comision_diaria
        
        st.metric("Ventas/día", ventas_diarias)
        st.metric("Revenue/día", f"${revenue_bruto_diario:.2f}")
        st.metric("Ganancia/día", f"${ganancia_neta_diaria:.2f}")
    
    # Métricas clave
    st.markdown("### 📈 Métricas Clave")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        roi_diario = ((ganancia_neta_diaria / costo_ads_diario) * 100) if costo_ads_diario > 0 else 0
        st.metric("ROI", f"{roi_diario:.1f}%")
    with col2:
        roas = (revenue_bruto_diario / costo_ads_diario) if costo_ads_diario > 0 else 0
        st.metric("ROAS", f"{roas:.2f}")
    with col3:
        margen = ((ganancia_neta_diaria / revenue_bruto_diario) * 100) if revenue_bruto_diario > 0 else 0
        st.metric("Margen", f"{margen:.1f}%")
    with col4:
        breakeven = precio_venta * (1 - comision_plataforma/100)
        st.metric("Break-even CPA", f"${breakeven:.2f}")
    
    # Proyección del período
    st.markdown("### 📅 Proyección del Período")
    
    revenue_periodo = revenue_bruto_diario * dias_proyeccion
    costo_periodo = costo_ads_diario * dias_proyeccion
    ganancia_periodo = ganancia_neta_diaria * dias_proyeccion
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(f"Revenue {dias_proyeccion} días", f"${revenue_periodo:,.2f}")
    with col2:
        st.metric(f"Costos {dias_proyeccion} días", f"${costo_periodo:,.2f}")
    with col3:
        st.metric(f"Ganancia {dias_proyeccion} días", f"${ganancia_periodo:,.2f}")
    
    # Análisis y recomendaciones
    st.markdown("### 💡 Análisis")
    
    if ganancia_neta_diaria > 0:
        st.success("✅ PRODUCTO RENTABLE")
        
        if roas >= 3.0:
            st.success("🔥 ROAS EXCELENTE (3.0+) - Escalar inmediatamente")
        elif roas >= 2.0:
            st.info("👍 ROAS BUENO (2.0+) - Continuar optimizando")
        else:
            st.warning("⚠️ ROAS BAJO (<2.0) - Optimizar urgente")
        
        # Proyección anual
        ganancia_anual = ganancia_neta_diaria * 365
        st.info(f"💰 **Proyección anual:** ${ganancia_anual:,.2f}")
        
        # Mostrar siguiente paso
        mostrar_siguiente_paso("🧮 Calculadora de Ganancias")
        
    else:
        st.error("❌ PRODUCTO NO RENTABLE")
        
        if cpa_estimado > (precio_venta * 0.5):
            st.warning("CPA muy alto - Reducir costos")
        if conversion_rate < 1.0:
            st.warning("Conversión muy baja - Optimizar landing")

# Mostrar siguiente paso si no hay cálculo previo
if menu == "🧮 Calculadora de Ganancias" and ganancia_neta_diaria == 0:
    mostrar_siguiente_paso("🧮 Calculadora de Ganancias")

# ==========================================
# FOOTER SIMPLE
# ==========================================

st.markdown("---")
st.markdown("### 💰 Mega Buscador PEV - Herramienta para Generar Dinero")
st.markdown("**Objetivo:** Encontrar productos digitales exitosos y copiarlos para generar ingresos.")