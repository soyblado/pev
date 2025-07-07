# mega_buscador_pev_simple.py
# HERRAMIENTA SIMPLE Y FUNCIONAL PARA ENCONTRAR PRODUCTOS DIGITALES RENTABLES

import streamlit as st
import time
import random
import re
import pandas as pd
import matplotlib.pyplot as plt
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from deep_translator import GoogleTranslator
from datetime import datetime, timedelta
from webdriver_manager.chrome import ChromeDriverManager

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración del sistema
CONFIG = {
    "timeout_seconds": 20,
    "max_anuncios": 50,
    "retry_attempts": 3,
    "delay_between_requests": 0.5,
    "scroll_attempts": 3,
    "min_text_length": 20
}

# Definir PAIS_IDIOMA_PRINCIPAL al inicio del archivo
PAIS_IDIOMA_PRINCIPAL = {
    'US': 'english', 'CA': 'english', 'GB': 'english', 'AU': 'english', 'NZ': 'english',
    'BR': 'portuguese', 'FR': 'french', 'DE': 'german', 'NL': 'german',
    'ES': 'spanish', 'MX': 'spanish', 'AR': 'spanish', 'CO': 'spanish', 'CL': 'spanish', 'PE': 'spanish',
    'JP': 'japanese', 'KR': 'korean', 'CN': 'chinese', 'ZA': 'english', 'IN': 'english', 'ID': 'english'
}

# ==========================================
# CONFIGURACIÓN INICIAL
# ==========================================

st.set_page_config(
    page_title="Mega Buscador PEV",
    page_icon="💰",
    layout="wide"
)

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
    """Crea y retorna un driver de Selenium Chrome configurado para scraping con opciones anti-bloqueo."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-images")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f"--user-agent={random.choice(UA_LIST)}")
    
    # Usar webdriver-manager para manejar ChromeDriver automáticamente
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def evaluar_facilidad_copia(descripcion):
    """Evalúa qué tan fácil es copiar el producto a partir de su descripción."""
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
    """Analiza el potencial de rentabilidad de un producto según el número de anuncios activos."""
    
    if total_anuncios >= 1000:
        return {
            "estado": "🔴 SATURADO",
            "accion": "EVITAR - Muy competido",
            "prioridad": 5
        }
    elif total_anuncios >= 500:
        return {
            "estado": "🟡 ALTA COMPETENCIA",
            "accion": "CUIDADO - Evaluar bien",
            "prioridad": 4
        }
    elif total_anuncios >= 100:
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
    """Traduce una lista de palabras clave al idioma destino usando GoogleTranslator con cache."""
    if idioma_destino == "spanish":
        return palabras
    
    # Inicializar cache si no existe
    if 'traducciones_cache' not in st.session_state:
        st.session_state.traducciones_cache = {}
    
    iso_code = LANG2ISO.get(idioma_destino, "en")
    translator = GoogleTranslator(source="es", target=iso_code)
    
    traducidas = []
    for palabra in palabras:
        # Crear clave de cache
        cache_key = f"{iso_code}_{palabra}"
        
        # Verificar si ya está en cache
        if cache_key in st.session_state.traducciones_cache:
            traducidas.append(st.session_state.traducciones_cache[cache_key])
            continue
        
        try:
            traducida = translator.translate(palabra)
            traducidas.append(traducida)
            # Guardar en cache
            st.session_state.traducciones_cache[cache_key] = traducida
            time.sleep(CONFIG["delay_between_requests"])
        except Exception as e:
            logger.warning(f"Error traduciendo '{palabra}': {e}")
            st.warning(f"Error traduciendo '{palabra}': {e}")
            traducidas.append(palabra)
    
    return traducidas

def contar_anuncios(keyword, country):
    """Cuenta el número de anuncios activos en Facebook Ads Library para una keyword y país dados."""
    # Validación de parámetros
    if not keyword or not country:
        logger.error("Keyword y país son requeridos")
        st.error("Keyword y país son requeridos")
        return 0
    
    start_time = time.time()
    logger.info(f"Contando anuncios para '{keyword}' en {country}")
    
    driver = get_driver()
    try:
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered&media_type=all"
        driver.get(url)
        
        wait = WebDriverWait(driver, CONFIG["timeout_seconds"])
        
        # Múltiples selectores como fallback
        selectors = [
            "//div[contains(text(), 'result')]",
            "//div[contains(text(), 'anuncio')]",
            "//div[contains(text(), 'ad')]",
            "//div[contains(text(), 'ads')]"
        ]
        
        result_text = ""
        for selector in selectors:
            try:
                result_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                result_text = result_element.text
                break
            except TimeoutException:
                continue
        
        if result_text:
            numbers = re.findall(r'\d{1,3}(?:,\d{3})*', result_text)
            if numbers:
                count = int(numbers[0].replace(',', ''))
                execution_time = time.time() - start_time
                logger.info(f"Encontrados {count} anuncios en {execution_time:.2f} segundos")
                return count
            else:
                logger.warning(f"No se encontraron números en el texto: {result_text}")
                return 0
        else:
            logger.warning(f"No se encontró elemento de resultados para '{keyword}' en {country}")
            return 0
                
    except Exception as e:
        logger.error(f"Error contando anuncios para '{keyword}' en {country}: {e}")
        st.error(f"Error contando anuncios: {e}")
        # Actualizar métricas de errores
        st.session_state.metricas_rendimiento['errores'] += 1
        return 0
    finally:
        driver.quit()
        time.sleep(CONFIG["delay_between_requests"])

def obtener_anuncios(keyword, country, max_anuncios=15):
    """Obtiene anuncios detallados de Facebook Ads Library para una keyword y país, hasta un máximo dado."""
    # Validación de parámetros
    if not keyword or not country:
        logger.error("Keyword y país son requeridos")
        st.error("Keyword y país son requeridos")
        return []
    
    if max_anuncios > CONFIG["max_anuncios"]:
        max_anuncios = CONFIG["max_anuncios"]
        st.warning(f"Máximo de anuncios limitado a {CONFIG['max_anuncios']} para evitar bloqueos")
    
    start_time = time.time()
    logger.info(f"Obteniendo {max_anuncios} anuncios para '{keyword}' en {country}")
    
    driver = get_driver()
    anuncios = []
    
    try:
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered&media_type=all"
        driver.get(url)
        
        time.sleep(3)
        
        # Scroll para cargar contenido con configuración
        for _ in range(CONFIG["scroll_attempts"]):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='ad-card']")
        logger.info(f"Encontradas {len(cards)} tarjetas de anuncios")
        
        for i, card in enumerate(cards[:max_anuncios]):
            try:
                copy_element = card.find_element(By.CSS_SELECTOR, "[data-testid='ad-copy']")
                copy_text = copy_element.text
                
                if len(copy_text) > CONFIG["min_text_length"]:
                    # Evaluar facilidad de copia
                    facilidad = evaluar_facilidad_copia(copy_text)
                    
                    # Buscar enlace con múltiples selectores
                    link = "No disponible"
                    link_selectors = ["a[href]", "[data-testid='ad-creative-link']", "a"]
                    
                    for selector in link_selectors:
                        try:
                            link_element = card.find_element(By.CSS_SELECTOR, selector)
                            link = link_element.get_attribute("href")
                            if link:
                                break
                        except:
                            continue
                    
                    anuncios.append({
                        "Copy": copy_text[:200] + "..." if len(copy_text) > 200 else copy_text,
                        "Link": link,
                        "Dificultad": facilidad["dificultad"],
                        "Recomendación": facilidad["recomendacion"],
                        "Color": facilidad["color"]
                    })
                    
            except Exception as e:
                logger.warning(f"Error procesando anuncio {i+1}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error obteniendo anuncios para '{keyword}' en {country}: {e}")
        st.error(f"Error obteniendo anuncios: {e}")
        # Actualizar métricas de errores
        st.session_state.metricas_rendimiento['errores'] += 1
    finally:
        driver.quit()
        time.sleep(CONFIG["delay_between_requests"])
    
    execution_time = time.time() - start_time
    logger.info(f"Obtenidos {len(anuncios)} anuncios en {execution_time:.2f} segundos")
    return anuncios

def analizar_frases_reales(keyword, country, max_anuncios=30, min_frecuencia=2):
    """Analiza anuncios reales para extraer frases comunes que contengan la keyword y descubre competidores (páginas de Facebook)."""
    # Validación de parámetros
    if not keyword or not country:
        logger.error("Keyword y país son requeridos")
        st.error("Keyword y país son requeridos")
        return [], {}
    
    if max_anuncios > CONFIG["max_anuncios"]:
        max_anuncios = CONFIG["max_anuncios"]
        st.warning(f"Máximo de anuncios limitado a {CONFIG['max_anuncios']} para evitar bloqueos")
    
    start_time = time.time()
    logger.info(f"Analizando frases reales para '{keyword}' en {country}")
    
    driver = get_driver()
    frases_encontradas = []
    competidores = {}
    
    try:
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered&media_type=all"
        driver.get(url)
        time.sleep(random.uniform(3, 5))
        
        # Scroll mejorado con configuración
        for i in range(CONFIG["scroll_attempts"]):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
            time.sleep(random.uniform(2, 4))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(2, 4))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3, 5))
        
        cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='ad-copy']")
        logger.info(f"Encontradas {len(cards)} tarjetas para análisis de frases")
        
        # Extraer frases y competidores
        texts = []
        for i, card in enumerate(cards[:max_anuncios]):
            try:
                text = card.text.lower().strip()
                if len(text) > CONFIG["min_text_length"] and keyword.lower() in text:
                    texts.append(text)
                
                # Extraer nombre de página (competidor) con múltiples selectores
                try:
                    parent = card.find_element(By.XPATH, "../../..")
                    page_name = None
                    
                    # Múltiples selectores para encontrar el nombre de la página
                    page_selectors = [
                        '[data-testid="ad-creative-link"]',
                        'a[aria-label]',
                        '[data-testid="ad-creative-page-name"]',
                        '.ad-creative-page-name'
                    ]
                    
                    for selector in page_selectors:
                        try:
                            element = parent.find_element(By.CSS_SELECTOR, selector)
                            page_name = element.text or element.get_attribute('aria-label')
                            if page_name:
                                break
                        except:
                            continue
                    
                    if page_name:
                        competidores[page_name] = competidores.get(page_name, 0) + 1
                        
                except Exception as e:
                    logger.warning(f"Error extrayendo competidor del anuncio {i+1}: {e}")
                
                time.sleep(random.uniform(0.5, 1))
            except Exception as e:
                logger.warning(f"Error procesando anuncio {i+1} para frases: {e}")
                continue
        import re
        patterns = [
            rf"[^.!?]*{re.escape(keyword.lower())}[^.!?]*",
            rf"\b\w+\s+{re.escape(keyword.lower())}\s+\w+\b",
            rf"{re.escape(keyword.lower())}\s+en\s+\d+\s+días?",
            rf"cómo\s+[^.!?]*{re.escape(keyword.lower())}[^.!?]*",
            rf"método\s+[^.!?]*{re.escape(keyword.lower())}[^.!?]*",
            rf"guía\s+[^.!?]*{re.escape(keyword.lower())}[^.!?]*",
            rf"supera?\s+[^.!?]*{re.escape(keyword.lower())}[^.!?]*",
        ]
        frase_counts = {}
        for text in texts:
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    frase = re.sub(r'\s+', ' ', match.strip())
                    if 10 <= len(frase) <= 80:
                        frase_counts[frase] = frase_counts.get(frase, 0) + 1
        
        frases_ordenadas = sorted(frase_counts.items(), key=lambda x: x[1], reverse=True)
        frases_encontradas = [
            {"frase": frase, "frecuencia": freq}
            for frase, freq in frases_ordenadas[:15]
            if freq >= min_frecuencia
        ]
        
        execution_time = time.time() - start_time
        logger.info(f"Análisis completado en {execution_time:.2f} segundos. Encontradas {len(frases_encontradas)} frases y {len(competidores)} competidores")
        
    except Exception as e:
        logger.error(f"Error analizando frases reales para '{keyword}' en {country}: {e}")
        st.error(f"Error analizando frases reales: {e}")
        # Actualizar métricas de errores
        st.session_state.metricas_rendimiento['errores'] += 1
    finally:
        driver.quit()
        time.sleep(random.uniform(2, 4))
    
    return frases_encontradas, competidores

# ==========================================
# INTERFAZ STREAMLIT
# ==========================================

# --- NUEVA PANTALLA INICIAL SIMPLIFICADA ---
st.title("💰 Mega Buscador PEV")
st.markdown("### *Encuentra Productos Digitales Rentables para Copiar*")

# ==========================================
# MÓDULO 1: INICIO RÁPIDO
# ==========================================

if 'menu_seleccionado' not in st.session_state:
    st.session_state.menu_seleccionado = "🚀 Inicio Rápido"

menu = st.sidebar.radio(
    "Selecciona una opción:",
    [
        "🚀 Inicio Rápido",
        "📊 Análisis de Demanda",
        "🔍 Búsqueda de Productos", 
        "🕵️ Espionaje de Competidores",
        "🧮 Calculadora de Ganancias",
        "🎯 Analizador de Frases Reales"
    ],
    index=[
        "🚀 Inicio Rápido",
        "📊 Análisis de Demanda",
        "🔍 Búsqueda de Productos", 
        "🕵️ Espionaje de Competidores",
        "🧮 Calculadora de Ganancias",
        "🎯 Analizador de Frases Reales"
    ].index(st.session_state.menu_seleccionado) if st.session_state.menu_seleccionado in [
        "🚀 Inicio Rápido",
        "📊 Análisis de Demanda",
        "🔍 Búsqueda de Productos", 
        "🕵️ Espionaje de Competidores",
        "🧮 Calculadora de Ganancias",
        "🎯 Analizador de Frases Reales"
    ] else 0,
    key='menu_principal'
)

# Actualizar session state cuando cambie el menú
if menu != st.session_state.menu_seleccionado:
    st.session_state.menu_seleccionado = menu

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

if 'frases_seleccionadas' not in st.session_state:
    st.session_state.frases_seleccionadas = []

# Inicializar la bandera de stop_search si no existe
if 'stop_search' not in st.session_state:
    st.session_state['stop_search'] = False

# Métricas de rendimiento
if 'metricas_rendimiento' not in st.session_state:
    st.session_state.metricas_rendimiento = {
        'total_busquedas': 0,
        'tiempo_total': 0,
        'errores': 0,
        'anuncios_encontrados': 0
    }

# Inicializar historiales en session_state si no existen
if 'historial_demanda' not in st.session_state:
    st.session_state['historial_demanda'] = []
if 'historial_productos' not in st.session_state:
    st.session_state['historial_productos'] = []
if 'historial_frases' not in st.session_state:
    st.session_state['historial_frases'] = []
if 'historial_competidores' not in st.session_state:
    st.session_state['historial_competidores'] = []

# ==========================================
# FUNCIÓN DE NAVEGACIÓN
# ==========================================

def mostrar_siguiente_paso(menu_actual):
    """Muestra sugerencia del siguiente paso en el proceso, solo como diálogo informativo, sin botón de navegación que borre el estado."""
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
        },
        "🎯 Analizador de Frases Reales": {
            "siguiente": "🔍 Búsqueda de Productos",
            "accion": "Usa las frases encontradas para buscar productos",
            "descripcion": "Aplica las frases reales encontradas para buscar productos específicos"
        }
    }
    if menu_actual in pasos_proceso:
        info_siguiente = pasos_proceso[menu_actual]
        st.markdown("---")
        st.markdown("### 🚀 Siguiente Paso Recomendado")
        st.info(f"**{info_siguiente['siguiente']}**: {info_siguiente['descripcion']}")

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

# Métricas de Rendimiento
with st.sidebar.expander("📊 Métricas de Rendimiento", expanded=False):
    metricas = st.session_state.metricas_rendimiento
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Búsquedas", metricas['total_busquedas'])
        st.metric("Anuncios", metricas['anuncios_encontrados'])
    with col2:
        st.metric("Tiempo Total", f"{metricas['tiempo_total']}s")
        st.metric("Errores", metricas['errores'])
    
    if st.button("🔄 Resetear Métricas", key="reset_metricas"):
        st.session_state.metricas_rendimiento = {
            'total_busquedas': 0,
            'tiempo_total': 0,
            'errores': 0,
            'anuncios_encontrados': 0
        }
        st.success("Métricas reseteadas!")
        st.rerun()

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
        "🧮 Calculadora de Ganancias",
        "🎯 Analizador de Frases Reales"
    ],
    index=[
        "🚀 Inicio Rápido",
        "📊 Análisis de Demanda",
        "🔍 Búsqueda de Productos", 
        "🕵️ Espionaje de Competidores",
        "🧮 Calculadora de Ganancias",
        "🎯 Analizador de Frases Reales"
    ].index(st.session_state.menu_seleccionado) if st.session_state.menu_seleccionado in [
        "🚀 Inicio Rápido",
        "📊 Análisis de Demanda",
        "🔍 Búsqueda de Productos", 
        "🕵️ Espionaje de Competidores",
        "🧮 Calculadora de Ganancias",
        "🎯 Analizador de Frases Reales"
    ] else 0,
    key='menu_principal'
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
        keywords_input = st.text_area("Keywords manuales:", "ebook, curso, guía")
    
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
    
    busqueda_multilingue = st.checkbox('¿Buscar también en otros idiomas? (multilingüe)', value=False)
    
    stop_placeholder = st.empty()
    if st.button("📊 Analizar Demanda", type="primary"):
        st.session_state['stop_search'] = False
        if keywords_input and paises_selected:
            keywords = [kw.strip() for kw in keywords_input.split(",")]
            
            with st.spinner("Analizando demanda..."):
                resultados = []
                
                for pais in paises_selected:
                    # Mostrar botón detener
                    if stop_placeholder.button("Detener búsqueda", key=f"stop_search_demanda_{pais}"):
                        st.session_state['stop_search'] = True
                    if st.session_state.get('stop_search'):
                        st.warning("Búsqueda detenida por el usuario.")
                        break
                    if busqueda_multilingue:
                        for idioma in LANGS.values():
                            keywords_traducidas = traducir_palabras(keywords, idioma)
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
                    else:
                        idioma_pais = PAIS_IDIOMA_PRINCIPAL.get(pais, 'english')
                        keywords_traducidas = traducir_palabras(keywords, idioma_pais)
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
            
            if st.session_state.get('stop_search'):
                st.info("Puedes ajustar tus parámetros y volver a buscar.")
            elif resultados:
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

                # Análisis de demanda:
                if 'analisis_demanda_historial' not in st.session_state:
                    st.session_state.analisis_demanda_historial = []
                st.session_state.analisis_demanda_historial.append(resultados)
            else:
                st.error("No se obtuvieron resultados")
        else:
            st.error("Completa todos los campos")

    # Al finalizar cada análisis, agrega los resultados al historial correspondiente
    # Análisis de demanda:
    if menu == "📊 Análisis de Demanda" and 'analisis_demanda_resultados' in st.session_state and st.session_state.analisis_demanda_resultados:
        st.session_state['historial_demanda'].append(st.session_state.analisis_demanda_resultados)

# ==========================================
# MÓDULO 3: BÚSQUEDA DE PRODUCTOS
# ==========================================

elif menu == "🔍 Búsqueda de Productos":
    st.header("🔍 Búsqueda Detallada de Productos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        idioma_busqueda = st.selectbox("Idioma:", list(LANGS.keys()))
        
        # Pre-cargar países de alta demanda si están disponibles
        default_countries = st.session_state.paises_alta_demanda if st.session_state.paises_alta_demanda else ["US", "BR", "GB"]
        
        paises_busqueda = st.multiselect(
            "Países objetivo:",
            ALL_COUNTRIES,
            default=default_countries,
            format_func=lambda x: COUNTRY2NAME[x],
            help="Países pre-cargados del análisis de demanda anterior" if st.session_state.paises_alta_demanda else None
        )
    
    with col2:
        keywords_text = st.text_area("Keywords personalizadas:", ", ".join(st.session_state.keywords_exitosas))
    
    col1, col2 = st.columns(2)
    with col1:
        min_anuncios = st.number_input("Mínimo anuncios:", min_value=1, value=30)
    with col2:
        solo_faciles = st.checkbox("Solo productos fáciles de copiar", value=True)
    
    # En el módulo de Búsqueda de Productos, después de seleccionar países:
    busqueda_multilingue_prod = st.checkbox('¿Buscar también en otros idiomas? (multilingüe)', value=False, key='busqueda_multilingue_prod')
    
    stop_placeholder_prod = st.empty()
    if st.button("🔍 Buscar Productos", type="primary"):
        st.session_state['stop_search'] = False
        st.session_state.tiempo_inicio_busqueda = time.time()
        if keywords_text and paises_busqueda:
            keywords = [kw.strip() for kw in keywords_text.split(",")]
            with st.spinner("Analizando demanda y buscando productos..."):
                todos_productos = []
                resultados_conteo = []
                for pais in paises_busqueda:
                    # Mostrar botón detener
                    if stop_placeholder_prod.button("Detener búsqueda", key=f"stop_search_prod_{pais}"):
                        st.session_state['stop_search'] = True
                    if st.session_state.get('stop_search'):
                        st.warning("Búsqueda detenida por el usuario.")
                        break
                    if busqueda_multilingue_prod:
                        for idioma in LANGS.values():
                            keywords_pais = traducir_palabras(keywords, idioma)
                            for keyword in keywords_pais:
                                count = contar_anuncios(keyword, pais)
                                rentabilidad = analizar_rentabilidad(count)
                                resultados_conteo.append({
                                    "País": COUNTRY2NAME[pais],
                                    "Keyword": keyword,
                                    "Anuncios": count,
                                    "Estado": rentabilidad["estado"]
                                })
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
                    else:
                        idioma_pais = PAIS_IDIOMA_PRINCIPAL.get(pais, 'english')
                        keywords_pais = traducir_palabras(keywords, idioma_pais)
                        for keyword in keywords_pais:
                            count = contar_anuncios(keyword, pais)
                            rentabilidad = analizar_rentabilidad(count)
                            resultados_conteo.append({
                                "País": COUNTRY2NAME[pais],
                                "Keyword": keyword,
                                "Anuncios": count,
                                "Estado": rentabilidad["estado"]
                            })
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
                
                if st.session_state.get('stop_search'):
                    st.info("Puedes ajustar tus parámetros y volver a buscar.")
                elif todos_productos:
                    # Guardar productos en session state
                    st.session_state.productos_encontrados = todos_productos
                    # Actualizar contador del torneo
                    st.session_state.ofertas_encontradas += len(todos_productos)
                    
                    # Actualizar métricas de rendimiento
                    st.session_state.metricas_rendimiento['total_busquedas'] += 1
                    st.session_state.metricas_rendimiento['anuncios_encontrados'] += len(todos_productos)
                    
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
                                link_value = producto['Link']
                                if isinstance(link_value, str) and link_value != "No disponible":
                                    st.link_button("🔗 Ver", link_value)
                        
                        st.markdown("---")
                    
                    # Resumen mejorado
                    dificultad_series = pd.Series(df_filtrado["Dificultad"])
                    facilidad_counts = dificultad_series.value_counts()
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
                    
                    if faciles is not None and faciles >= 5:
                        st.success("🔥 EXCELENTE: Múltiples productos fáciles de copiar con alta demanda")
                    elif faciles is not None and faciles >= 2:
                        st.info("✅ BUENO: Algunas buenas oportunidades encontradas")
                    else:
                        st.warning("⚠️ POCAS OPCIONES: Considera ajustar filtros o probar otras keywords")
                    
                    # Opción de exportar a CSV
                    if st.button('Exportar a CSV'):
                        df_productos.to_csv('productos_encontrados.csv', index=False)
                        st.success('Archivo productos_encontrados.csv exportado.')
                    
                    # Mostrar siguiente paso
                    mostrar_siguiente_paso("🔍 Búsqueda de Productos")
                    
                    # Alerta de velocidad según el curso
                    if len(df_filtrado) > 0:
                        st.warning("""
                        ⚡ **RECUERDA DEL CURSO:** Las ofertas virales pueden saturarse en 7-15 días.
                        Lanza tu oferta modelada en menos de 24 horas para maximizar ganancias.
                        """)
                        
                        # Mostrar tiempo de ejecución
                        if 'tiempo_inicio_busqueda' in st.session_state:
                            tiempo_total = time.time() - st.session_state.tiempo_inicio_busqueda
                            st.info(f"⏱️ Búsqueda completada en {tiempo_total:.2f} segundos")
                            st.session_state.metricas_rendimiento['tiempo_total'] += int(tiempo_total)

                    # Búsqueda de productos:
                    if 'productos_historial' not in st.session_state:
                        st.session_state.productos_historial = []
                    st.session_state.productos_historial.append(todos_productos)
                
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

    # Al finalizar cada análisis, agrega los resultados al historial correspondiente
    # Búsqueda de productos:
    if menu == "🔍 Búsqueda de Productos" and 'productos_encontrados' in st.session_state and st.session_state.productos_encontrados:
        st.session_state['historial_productos'].append(st.session_state.productos_encontrados)

# ==========================================
# MÓDULO 4: ESPIONAJE DE COMPETIDORES
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

                    # Espionaje de competidores:
                    if 'competidores_historial' not in st.session_state:
                        st.session_state.competidores_historial = []
                    st.session_state.competidores_historial.append(resultados_comp)
                
                else:
                    st.warning("No se encontraron competidores con suficiente actividad publicitaria")
        else:
            st.error("Ingresa al menos un competidor")

    # Al finalizar cada análisis, agrega los resultados al historial correspondiente
    # Competidores:
    if menu == "🕵️ Espionaje de Competidores" and 'competidores_analizados' in st.session_state and st.session_state.competidores_analizados:
        st.session_state['historial_competidores'].append(st.session_state.competidores_analizados)

# ==========================================
# MÓDULO 5: CALCULADORA DE GANANCIAS
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
# MÓDULO 6: ANALIZADOR DE FRASES REALES
# ==========================================

elif menu == "🎯 Analizador de Frases Reales":
    st.header("🎯 Analizador de Frases Reales")
    st.markdown("""
    Analiza anuncios reales para encontrar frases exitosas que contengan tu keyword.
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
                frases_reales, competidores = analizar_frases_reales(keyword_analisis, pais_analisis, max_anuncios_analisis, min_frecuencia)
                if frases_reales:
                    st.markdown(f"### 🎯 Frases Reales Encontradas para '{keyword_analisis}'")
                    st.markdown(f"*Analizados en {COUNTRY2NAME[pais_analisis]} - Mínimo {min_frecuencia} apariciones*")
                    frases_filtradas = [f for f in frases_reales if f["frecuencia"] >= min_frecuencia]
                    if frases_filtradas:
                        st.markdown("#### 📝 Frases que puedes usar:")
                        for i, frase_data in enumerate(frases_filtradas, 1):
                            frase = frase_data["frase"]
                            freq = frase_data["frecuencia"]
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
                                        if frase not in st.session_state.frases_seleccionadas:
                                            st.session_state.frases_seleccionadas.append(frase)
                                            st.success(f"Frase agregada: {frase}")
                                        else:
                                            st.info("Ya está seleccionada")
                        if st.session_state.frases_seleccionadas:
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
                            st.info("💡 Estas frases se cargarán automáticamente en 'Búsqueda de Productos'")
                    else:
                        st.warning(f"No se encontraron frases con frecuencia mínima de {min_frecuencia}")
                        st.markdown("**Intenta:**")
                        st.markdown("- Reducir la frecuencia mínima")
                        st.markdown("- Probar en otro país")
                        st.markdown("- Usar una keyword más general")
                else:
                    st.error(f"No se encontraron frases para '{keyword_analisis}' en {COUNTRY2NAME[pais_analisis]}")
                    st.markdown("**Posibles causas:**")
                    st.markdown("- La keyword no tiene suficientes anuncios")
                    st.markdown("- Prueba con una palabra más común")
                    st.markdown("- Intenta en otro país con más actividad publicitaria")

                    # Analizador de frases reales:
                    if 'frases_historial' not in st.session_state:
                        st.session_state.frases_historial = []
                    st.session_state.frases_historial.append(frases_reales)

                    # Después de mostrar las frases reales encontradas, mostrar la lista de competidores descubiertos:
                    if competidores:
                        st.markdown('### 🕵️ Posibles Competidores Descubiertos')
                        competidores_ordenados = sorted(competidores.items(), key=lambda x: x[1], reverse=True)
                        if 'competidores_descubiertos' not in st.session_state:
                            st.session_state['competidores_descubiertos'] = {}
                        for nombre, cantidad in competidores_ordenados:
                            col1, col2, col3 = st.columns([4, 1, 1])
                            with col1:
                                st.markdown(f'- **{nombre}** ({cantidad} anuncios)')
                            with col2:
                                if st.button('⭐ Relevante', key=f'relevante_{nombre}'):
                                    st.session_state['competidores_descubiertos'][nombre] = cantidad
                                    st.success(f'Competidor marcado como relevante: {nombre}')
                            with col3:
                                if st.button('❌ Eliminar', key=f'eliminar_{nombre}'):
                                    competidores.pop(nombre, None)
                                    st.session_state['competidores_descubiertos'].pop(nombre, None)
                                    st.warning(f'Competidor eliminado: {nombre}')
                        st.info('Puedes marcar como relevantes los competidores que te interesen. Se guardarán para futuras búsquedas.')
        else:
            st.error("Por favor, ingresa una keyword para analizar")

    # Al finalizar cada análisis, agrega los resultados al historial correspondiente
    # Frases reales:
    if menu == "🎯 Analizador de Frases Reales" and 'frases_seleccionadas' in st.session_state and st.session_state.frases_seleccionadas:
        st.session_state['historial_frases'].append(st.session_state.frases_seleccionadas)

# ==========================================
# FOOTER SIMPLE
# ==========================================

st.markdown("---")
st.markdown("### 💰 Mega Buscador PEV - Herramienta para Generar Dinero")
st.markdown("**Objetivo:** Encontrar productos digitales exitosos y copiarlos para generar ingresos.")

# 1. RESUMEN RÁPIDO EN LA BARRA LATERAL
with st.sidebar.expander("📊 Resumen Rápido de la Sesión", expanded=True):
    if 'analisis_demanda_historial' not in st.session_state:
        st.session_state.analisis_demanda_historial = []
    if 'productos_historial' not in st.session_state:
        st.session_state.productos_historial = []
    if 'frases_historial' not in st.session_state:
        st.session_state.frases_historial = []
    if 'competidores_historial' not in st.session_state:
        st.session_state.competidores_historial = []
    # Mostrar resumen de cada módulo
    st.markdown("**Último análisis de demanda:**")
    if st.session_state.analisis_demanda_historial:
        last = st.session_state.analisis_demanda_historial[-1]
        st.write(f"{len(last)} combinaciones, países: {', '.join(set([r['País'] for r in last]))}")
    else:
        st.write("No hay análisis de demanda aún.")
    st.markdown("**Últimos productos encontrados:**")
    if st.session_state.productos_historial:
        last = st.session_state.productos_historial[-1]
        st.write(f"{len(last)} productos, países: {', '.join(set([p['País'] for p in last]))}")
    else:
        st.write("No hay productos aún.")
    st.markdown("**Frases seleccionadas:**")
    if st.session_state.frases_seleccionadas:
        for frase in st.session_state.frases_seleccionadas:
            st.write(f"- {frase}")
    else:
        st.write("No hay frases seleccionadas.")
    st.markdown("**Últimos competidores analizados:**")
    if st.session_state.competidores_historial:
        last = st.session_state.competidores_historial[-1]
        st.write(f"{len(last)} competidores")
    else:
        st.write("No hay competidores aún.")
    # 4. Exportar historial
    if st.button('Exportar historial a CSV'):
        import pandas as pd
        # Unir todos los historiales en un solo DataFrame
        all_data = []
        for h in st.session_state.analisis_demanda_historial:
            all_data.extend(h)
        for h in st.session_state.productos_historial:
            all_data.extend(h)
        for h in st.session_state.competidores_historial:
            all_data.extend(h)
        if all_data:
            df_hist = pd.DataFrame(all_data)
            df_hist.to_csv('historial_completo.csv', index=False)
            st.success('Historial exportado a historial_completo.csv')
        else:
            st.warning('No hay datos para exportar.')
    
    # Limpiar cache de traducciones
    if st.button('🗑️ Limpiar Cache'):
        if 'traducciones_cache' in st.session_state:
            del st.session_state.traducciones_cache
        st.success('Cache de traducciones limpiado!')

# 3. SECCIÓN DE COMPARACIÓN DE RESULTADOS
if st.sidebar.checkbox('Comparar análisis de demanda', value=False):
    st.markdown('## 📊 Comparación de Análisis de Demanda')
    if len(st.session_state.analisis_demanda_historial) > 1:
        import pandas as pd
        dfs = [pd.DataFrame(h) for h in st.session_state.analisis_demanda_historial]
        for i, df in enumerate(dfs):
            st.markdown(f'### Análisis #{i+1}')
            st.dataframe(df)
        # Gráfico comparativo simple
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        for i, df in enumerate(dfs):
            ax.plot(df['País'], df['Anuncios'], label=f'Análisis {i+1}')
        ax.set_ylabel('Anuncios')
        ax.set_xlabel('País')
        ax.legend()
        st.pyplot(fig)
    else:
        st.info('Realiza al menos dos análisis para comparar.')

# Mostrar historial en la barra lateral
with st.sidebar.expander("🕓 Historial de la sesión", expanded=False):
    st.markdown("<br>", unsafe_allow_html=True)
    filtro_tipo = st.selectbox("Filtrar por tipo", ["Todos", "Demanda", "Productos", "Frases", "Competidores"], key="filtro_historial_tipo")
    st.divider()
    if filtro_tipo in ["Todos", "Demanda"]:
        st.markdown("### 🔎 <b>Análisis de Demanda</b>", unsafe_allow_html=True)
        for i, h in enumerate(st.session_state['historial_demanda'], 1):
            if h and isinstance(h, list) and len(h) > 0:
                resumen = h[0]
                keyword = resumen.get("Keyword", "-")
                pais = resumen.get("País", "-")
                fecha = resumen.get("Fecha", datetime.now().strftime("%Y-%m-%d"))
                st.markdown(f"**{i}. Keyword:** {keyword} | **País:** {pais} | **Fecha:** {fecha} | **Resultados:** {len(h)}")
                with st.expander(f"Ver detalles demanda #{i}", expanded=False):
                    df = pd.DataFrame(h)
                    st.dataframe(df, use_container_width=True)
            st.write("")
        st.divider()
    if filtro_tipo in ["Todos", "Productos"]:
        st.markdown("### 🛒 <b>Búsqueda de Productos</b>", unsafe_allow_html=True)
        for i, h in enumerate(st.session_state['historial_productos'], 1):
            if h and isinstance(h, list) and len(h) > 0:
                resumen = h[0]
                keyword = resumen.get("Keyword", "-")
                pais = resumen.get("País", "-")
                fecha = resumen.get("Fecha", datetime.now().strftime("%Y-%m-%d"))
                st.markdown(f"**{i}. Keyword:** {keyword} | **País:** {pais} | **Fecha:** {fecha} | **Productos:** {len(h)}")
                with st.expander(f"Ver detalles productos #{i}", expanded=False):
                    df = pd.DataFrame(h)
                    st.dataframe(df, use_container_width=True)
            st.write("")
        st.divider()
    if filtro_tipo in ["Todos", "Frases"]:
        st.markdown("### 📝 <b>Frases Reales</b>", unsafe_allow_html=True)
        for i, h in enumerate(st.session_state['historial_frases'], 1):
            if h and isinstance(h, list) and len(h) > 0:
                frase = h[0] if isinstance(h[0], str) else h[0].get("frase", "-")
                st.markdown(f"**{i}. Ejemplo:** {frase} | **Total frases:** {len(h)}")
                with st.expander(f"Ver detalles frases #{i}", expanded=False):
                    st.write(h)
            st.write("")
        st.divider()
    if filtro_tipo in ["Todos", "Competidores"]:
        st.markdown("### 🕵️ <b>Competidores Analizados</b>", unsafe_allow_html=True)
        for i, h in enumerate(st.session_state['historial_competidores'], 1):
            if h and isinstance(h, list) and len(h) > 0:
                nombre = h[0] if isinstance(h[0], str) else h[0].get("nombre", "-")
                st.markdown(f"**{i}. Ejemplo:** {nombre} | **Total competidores:** {len(h)}")
                with st.expander(f"Ver detalles competidores #{i}", expanded=False):
                    st.write(h)
            st.write("")
        st.divider()
    # Exportar historial a CSV
    if st.button('Exportar historial completo a CSV'):
        import pandas as pd
        all_data = []
        for h in st.session_state['historial_demanda']:
            all_data.extend(h)
        for h in st.session_state['historial_productos']:
            all_data.extend(h)
        for h in st.session_state['historial_competidores']:
            all_data.extend(h)
        if all_data:
            df_hist = pd.DataFrame(all_data)
            df_hist.to_csv('historial_completo.csv', index=False)
            st.success('Historial exportado a historial_completo.csv')
        else:
            st.warning('No hay datos para exportar.')