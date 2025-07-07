# mega_buscador_pev_viral_completo.py
# HERRAMIENTA AVANZADA DE ESPIONAJE VIRAL PARA PRODUCTOS DIGITALES

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
import threading

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# 📦 CONFIGURACIÓN DEL SISTEMA
# ==========================================

CONFIG = {
    "timeout_seconds": 20,
    "max_anuncios": 50,
    "retry_attempts": 3,
    "delay_between_requests": 0.5,
    "scroll_attempts": 3,
    "min_text_length": 20
}

# Pool de drivers para optimización
DRIVER_POOL = []
DRIVER_LOCK = threading.Lock()
MAX_DRIVERS = 3

# Rate limiting
class RateLimiter:
    def __init__(self, max_requests_per_minute=30):
        self.max_requests = max_requests_per_minute
        self.requests = []
    
    def wait_if_needed(self):
        now = time.time()
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = 60 - (now - self.requests[0])
            if sleep_time > 0:
                logger.info(f"Rate limit alcanzado. Esperando {sleep_time:.2f} segundos...")
                time.sleep(sleep_time)
        
        self.requests.append(now)

rate_limiter = RateLimiter(max_requests_per_minute=25)

# ==========================================
# 🌍 CONFIGURACIONES GEOGRÁFICAS
# ==========================================

PAIS_IDIOMA_PRINCIPAL = {
    'US': 'english', 'CA': 'english', 'GB': 'english', 'AU': 'english', 'NZ': 'english',
    'BR': 'portuguese', 'FR': 'french', 'DE': 'german', 'NL': 'german',
    'ES': 'spanish', 'MX': 'spanish', 'AR': 'spanish', 'CO': 'spanish', 'CL': 'spanish', 'PE': 'spanish',
    'JP': 'japanese', 'KR': 'korean', 'CN': 'chinese', 'ZA': 'english', 'IN': 'english', 'ID': 'english'
}

PAISES_RENTABLES = {
    "alta_rentabilidad": ["US", "CA", "GB", "DE", "NL", "FR", "AU", "NZ", "BR"],
    "buena_rentabilidad": ["JP", "KR", "CN", "ZA"],
    "rentabilidad_media": ["MX", "ES", "AR", "CO", "CL", "PE", "IN", "ID"]
}

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

# ==========================================
# 🚀 FUNCIONES DE ESPIONAJE VIRAL AVANZADO
# ==========================================

def analizar_duplicados_anuncios(keyword, country):
    """Detecta anuncios duplicados y calcula score de viralidad."""
    if not keyword or not country:
        mostrar_error("Keyword y país son requeridos")
        return {"anuncios_unicos": 0, "total_duplicados": 0, "score_viralidad": 0}
    
    rate_limiter.wait_if_needed()
    start_time = time.time()
    logger.info(f"Analizando duplicados para '{keyword}' en {country}")
    
    driver = None
    try:
        driver = get_driver_from_pool()
        
        url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country={country}&q={keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered&media_type=all"
        driver.get(url)
        
        smart_delay()
        
        duplicados_info = {}
        anuncios_unicos = 0
        total_duplicados = 0
        
        try:
            duplicado_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='ad-card']")
            
            for element in duplicado_elements:
                try:
                    copy_element = element.find_element(By.CSS_SELECTOR, "[data-testid='ad-copy']")
                    copy_text = copy_element.text[:100]
                    
                    duplicado_indicators = element.find_elements(By.CSS_SELECTOR, "[style*='purple'], [style*='yellow'], [style*='red']")
                    
                    if copy_text in duplicados_info:
                        duplicados_info[copy_text]['count'] += 1
                        total_duplicados += 1
                    else:
                        duplicados_info[copy_text] = {
                            'count': 1,
                            'has_duplicates': len(duplicado_indicators) > 0
                        }
                        anuncios_unicos += 1
                        
                except Exception as e:
                    logger.warning(f"Error procesando elemento de duplicado: {e}")
                    continue
            
            score_viralidad = calcular_score_viralidad(anuncios_unicos, total_duplicados)
            
            execution_time = time.time() - start_time
            logger.info(f"Análisis de duplicados completado en {execution_time:.2f} segundos")
            
            return {
                "anuncios_unicos": anuncios_unicos,
                "total_duplicados": total_duplicados,
                "score_viralidad": score_viralidad,
                "duplicados_detallados": duplicados_info
            }
            
        except Exception as e:
            logger.warning(f"No se pudieron detectar duplicados específicos: {e}")
            total_anuncios = len(duplicado_elements)
            estimacion_duplicados = int(total_anuncios * 0.3)
            score_viralidad = calcular_score_viralidad(total_anuncios, estimacion_duplicados)
            
            return {
                "anuncios_unicos": total_anuncios,
                "total_duplicados": estimacion_duplicados,
                "score_viralidad": score_viralidad,
                "duplicados_detallados": {}
            }
                
    except Exception as e:
        mostrar_error(f"Error analizando duplicados para '{keyword}' en {country}", e)
        return {"anuncios_unicos": 0, "total_duplicados": 0, "score_viralidad": 0}
    finally:
        if driver:
            return_driver_to_pool(driver)

def calcular_score_viralidad(anuncios_unicos, total_duplicados):
    """Calcula score de viralidad basado en duplicados."""
    if anuncios_unicos == 0:
        return 0
    
    ratio_duplicados = total_duplicados / anuncios_unicos if anuncios_unicos > 0 else 0
    score_cantidad = min(anuncios_unicos / 10, 50)
    score_duplicados = min(ratio_duplicados * 25, 50)
    bonus_unicos = min(anuncios_unicos / 5, 20)
    
    score_total = score_cantidad + score_duplicados + bonus_unicos
    return min(score_total, 100)

def calcular_urgencia_lanzamiento(fecha_anuncio=None, duplicados=0):
    """Calcula urgencia de lanzamiento basado en metodología viral."""
    if not fecha_anuncio:
        if duplicados >= 10:
            return {
                "urgencia": "ALTA",
                "dias_restantes": 7,
                "mensaje": "🔥 VIRAL - Lanzar en 24-48 horas"
            }
        elif duplicados >= 5:
            return {
                "urgencia": "MEDIA", 
                "dias_restantes": 15,
                "mensaje": "⚡ ACTIVA - Lanzar en 3-7 días"
            }
        else:
            return {
                "urgencia": "BAJA",
                "dias_restantes": 30,
                "mensaje": "📊 ESTABLE - Lanzar cuando sea posible"
            }
    
    try:
        fecha_anuncio = datetime.strptime(fecha_anuncio, "%Y-%m-%d")
        dias_transcurridos = (datetime.now() - fecha_anuncio).days
        
        if dias_transcurridos <= 7:
            return {
                "urgencia": "ALTA",
                "dias_restantes": 7 - dias_transcurridos,
                "mensaje": f"🔥 VIRAL - Solo quedan {7 - dias_transcurridos} días"
            }
        elif dias_transcurridos <= 15:
            return {
                "urgencia": "MEDIA",
                "dias_restantes": 15 - dias_transcurridos,
                "mensaje": f"⚡ ACTIVA - Quedan {15 - dias_transcurridos} días"
            }
        else:
            return {
                "urgencia": "BAJA",
                "dias_restantes": 30 - dias_transcurridos,
                "mensaje": "📊 ESTABLE - Oferta madura"
            }
    except:
        return calcular_urgencia_lanzamiento(duplicados=duplicados)

def estimar_tiempo_modelado(tipo_producto, complejidad_funnel):
    """Estima tiempo de modelado basado en tipo de producto y complejidad."""
    tiempos_base = {
        "ebook": 2, "pdf": 2, "prompts": 1, "curso": 8, 
        "video": 12, "aplicacion": 24
    }
    
    multiplicadores_complejidad = {
        "FÁCIL": 1.0, "MEDIO": 1.5, "DIFÍCIL": 2.5
    }
    
    tiempo_base = tiempos_base.get(tipo_producto, 4)
    multiplicador = multiplicadores_complejidad.get(complejidad_funnel, 1.0)
    tiempo_estimado = tiempo_base * multiplicador
    
    return {
        "horas": tiempo_estimado,
        "tiempo_humano": f"{int(tiempo_estimado)} horas",
        "recomendacion": "Lanzar en 24h" if tiempo_estimado <= 8 else "Planificar 2-3 días"
    }

def analizar_funnel_completo(dominio):
    """Analiza el embudo completo de ventas."""
    if not dominio or dominio == "No disponible":
        return {
            "complejidad": "DESCONOCIDO",
            "landing_page": "No disponible",
            "checkout": "No disponible", 
            "upsells": [],
            "order_bombs": [],
            "tiempo_modelado": estimar_tiempo_modelado("ebook", "MEDIO")
        }
    
    rate_limiter.wait_if_needed()
    driver = None
    
    try:
        driver = get_driver_from_pool()
        driver.get(dominio)
        smart_delay()
        
        funnel_data = {
            "complejidad": "MEDIO",
            "landing_page": "Detectada",
            "checkout": "No detectado",
            "upsells": [],
            "order_bombs": [],
            "elementos_detectados": []
        }
        
        page_source = driver.page_source.lower()
        
        # Detectar checkout
        checkout_indicators = ["checkout", "pagar", "comprar", "buy now", "add to cart"]
        if any(indicator in page_source for indicator in checkout_indicators):
            funnel_data["checkout"] = "Detectado"
        
        # Detectar upsells
        upsell_indicators = ["upsell", "ofertas especiales", "bonus", "regalo", "oferta limitada"]
        for indicator in upsell_indicators:
            if indicator in page_source:
                funnel_data["upsells"].append(indicator)
        
        # Detectar order bombs
        order_bomb_indicators = ["order bump", "oferta adicional", "¿quieres también?", "añadir a tu pedido"]
        for indicator in order_bomb_indicators:
            if indicator in page_source:
                funnel_data["order_bombs"].append(indicator)
        
        # Determinar complejidad
        elementos_totales = len(funnel_data["upsells"]) + len(funnel_data["order_bombs"])
        if elementos_totales == 0:
            funnel_data["complejidad"] = "FÁCIL"
        elif elementos_totales <= 2:
            funnel_data["complejidad"] = "MEDIO"
        else:
            funnel_data["complejidad"] = "DIFÍCIL"
        
        # Estimar tiempo de modelado
        tipo_producto = "ebook"
        if "curso" in page_source or "video" in page_source:
            tipo_producto = "curso"
        elif "prompt" in page_source or "ai" in page_source:
            tipo_producto = "prompts"
        
        funnel_data["tiempo_modelado"] = estimar_tiempo_modelado(tipo_producto, funnel_data["complejidad"])
        
        return funnel_data
        
    except Exception as e:
        logger.warning(f"Error analizando funnel de {dominio}: {e}")
        return {
            "complejidad": "DESCONOCIDO",
            "landing_page": "Error al analizar",
            "checkout": "No detectado",
            "upsells": [],
            "order_bombs": [],
            "tiempo_modelado": estimar_tiempo_modelado("ebook", "MEDIO")
        }
    finally:
        if driver:
            return_driver_to_pool(driver)

def calcular_score_priorizacion(anuncios_duplicados, pais_objetivo, facilidad_modelado, tiempo_activo):
    """Calcula score de priorización usando algoritmo inteligente."""
    
    # 40% Anuncios duplicados
    score_duplicados = min(anuncios_duplicados / 10 * 40, 40)
    
    # 30% País objetivo (Brasil > US > Alemania > Francia)
    prioridad_paises = {
        "BR": 30, "US": 25, "DE": 20, "FR": 15,
        "CA": 20, "GB": 20, "AU": 15,
    }
    score_pais = prioridad_paises.get(pais_objetivo, 10)
    
    # 20% Facilidad de modelado
    facilidad_scores = {
        "FÁCIL": 20, "MEDIO": 15, "DIFÍCIL": 5, "DESCONOCIDO": 10
    }
    score_facilidad = facilidad_scores.get(facilidad_modelado, 10)
    
    # 10% Tiempo activo (más reciente = mejor)
    score_tiempo = max(10 - tiempo_activo, 0)
    
    score_total = score_duplicados + score_pais + score_facilidad + score_tiempo
    
    return {
        "score_total": score_total,
        "score_duplicados": score_duplicados,
        "score_pais": score_pais,
        "score_facilidad": score_facilidad,
        "score_tiempo": score_tiempo,
        "prioridad": "ALTA" if score_total >= 70 else "MEDIA" if score_total >= 50 else "BAJA"
    }

# ==========================================
# 🎨 FUNCIONES DE VISUALIZACIÓN VIRAL
# ==========================================

def mostrar_badge_viralidad(score):
    """Muestra un badge visual para el score de viralidad."""
    if score >= 80:
        return st.markdown(f"🔥 **VIRAL ({score:.0f})**", help="Score de viralidad muy alto - Lanzar inmediatamente")
    elif score >= 60:
        return st.markdown(f"⚡ **ACTIVO ({score:.0f})**", help="Score de viralidad alto - Lanzar en 24-48h")
    elif score >= 40:
        return st.markdown(f"📈 **CRECIENDO ({score:.0f})**", help="Score de viralidad medio - Evaluar")
    else:
        return st.markdown(f"📊 **ESTABLE ({score:.0f})**", help="Score de viralidad bajo - Investigar más")

def mostrar_badge_urgencia(urgencia_data):
    """Muestra un badge visual para la urgencia de lanzamiento."""
    urgencia = urgencia_data.get("urgencia", "BAJA")
    mensaje = urgencia_data.get("mensaje", "")
    
    if urgencia == "ALTA":
        return st.markdown(f"🚨 **{mensaje}**", help="Urgencia alta - Lanzar inmediatamente")
    elif urgencia == "MEDIA":
        return st.markdown(f"⚡ **{mensaje}**", help="Urgencia media - Lanzar pronto")
    else:
        return st.markdown(f"📅 **{mensaje}**", help="Urgencia baja - Planificar")

def mostrar_badge_prioridad(score_data):
    """Muestra un badge visual para la prioridad."""
    prioridad = score_data.get("prioridad", "BAJA")
    score_total = score_data.get("score_total", 0)
    
    if prioridad == "ALTA":
        return st.markdown(f"🎯 **ALTA PRIORIDAD ({score_total:.0f})**", help="Prioridad máxima - Enfocarse primero")
    elif prioridad == "MEDIA":
        return st.markdown(f"📋 **MEDIA PRIORIDAD ({score_total:.0f})**", help="Prioridad media - Considerar")
    else:
        return st.markdown(f"📝 **BAJA PRIORIDAD ({score_total:.0f})**", help="Prioridad baja - Revisar después")

def mostrar_metricas_duplicados(duplicados_data):
    """Muestra métricas de duplicados de forma visual."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Anuncios Únicos", duplicados_data.get("anuncios_unicos", 0))
    with col2:
        st.metric("Total Duplicados", duplicados_data.get("total_duplicados", 0))
    with col3:
        ratio = duplicados_data.get("total_duplicados", 0) / max(duplicados_data.get("anuncios_unicos", 1), 1)
        st.metric("Ratio Duplicados", f"{ratio:.2f}")
    with col4:
        score = duplicados_data.get("score_viralidad", 0)
        mostrar_badge_viralidad(score)

def mostrar_funnel_analysis(funnel_data):
    """Muestra análisis del funnel de forma visual."""
    with st.expander("🔍 Análisis del Funnel", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Complejidad:**")
            complejidad = funnel_data.get("complejidad", "DESCONOCIDO")
            if complejidad == "FÁCIL":
                st.success("🟢 FÁCIL - Copiar en 2-4 horas")
            elif complejidad == "MEDIO":
                st.warning("🟡 MEDIO - Copiar en 4-8 horas")
            else:
                st.error("🔴 DIFÍCIL - Copiar en 8+ horas")
            
            st.markdown("**⏱️ Tiempo de Modelado:**")
            tiempo = funnel_data.get("tiempo_modelado", {})
            st.info(f"🕐 {tiempo.get('tiempo_humano', 'N/A')}")
            st.caption(tiempo.get('recomendacion', ''))
        
        with col2:
            st.markdown("**🛒 Elementos Detectados:**")
            upsells = funnel_data.get("upsells", [])
            order_bombs = funnel_data.get("order_bombs", [])
            
            if upsells:
                st.markdown("**Upsells:**")
                for upsell in upsells:
                    st.markdown(f"- {upsell}")
            
            if order_bombs:
                st.markdown("**Order Bombs:**")
                for bomb in order_bombs:
                    st.markdown(f"- {bomb}")

def crear_tabla_resultados_viral(df_resultados):
    """Crea una tabla visual mejorada con métricas de espionaje viral."""
    if df_resultados.empty:
        st.warning("No hay resultados para mostrar")
        return
    
    # Agregar columnas de métricas virales si no existen
    if "Score_Viralidad" not in df_resultados.columns:
        df_resultados["Score_Viralidad"] = 0
    if "Urgencia" not in df_resultados.columns:
        df_resultados["Urgencia"] = "BAJA"
    if "Prioridad" not in df_resultados.columns:
        df_resultados["Prioridad"] = "BAJA"
    
    # Filtros
    st.markdown("### 🔍 Filtros Avanzados")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_score = st.slider("Score mínimo de viralidad:", 0, 100, 0)
    with col2:
        prioridad_filtro = st.selectbox("Prioridad mínima:", ["TODAS", "ALTA", "MEDIA", "BAJA"])
    with col3:
        urgencia_filtro = st.selectbox("Urgencia mínima:", ["TODAS", "ALTA", "MEDIA", "BAJA"])
    
    # Aplicar filtros
    df_filtrado = df_resultados.copy()
    
    if min_score > 0:
        df_filtrado = df_filtrado[df_filtrado["Score_Viralidad"] >= min_score]
    
    if prioridad_filtro != "TODAS":
        df_filtrado = df_filtrado[df_filtrado["Prioridad"] == prioridad_filtro]
    
    if urgencia_filtro != "TODAS":
        df_filtrado = df_filtrado[df_filtrado["Urgencia"] == urgencia_filtro]
    
    # Ordenamiento
    st.markdown("### 📊 Ordenar por:")
    orden = st.selectbox("Criterio de ordenamiento:", [
        "Score de Viralidad (Descendente)",
        "Anuncios (Descendente)", 
        "Prioridad (Alta → Baja)",
        "Urgencia (Alta → Baja)",
        "País (A-Z)"
    ])
    
    if "Viralidad" in orden:
        df_filtrado = df_filtrado.sort_values("Score_Viralidad", ascending=False)
    elif "Anuncios" in orden:
        df_filtrado = df_filtrado.sort_values("Anuncios", ascending=False)
    elif "Prioridad" in orden:
        prioridad_order = {"ALTA": 3, "MEDIA": 2, "BAJA": 1}
        df_filtrado["Prioridad_Order"] = df_filtrado["Prioridad"].map(prioridad_order)
        df_filtrado = df_filtrado.sort_values("Prioridad_Order", ascending=False)
        df_filtrado = df_filtrado.drop("Prioridad_Order", axis=1)
    elif "Urgencia" in orden:
        urgencia_order = {"ALTA": 3, "MEDIA": 2, "BAJA": 1}
        df_filtrado["Urgencia_Order"] = df_filtrado["Urgencia"].map(urgencia_order)
        df_filtrado = df_filtrado.sort_values("Urgencia_Order", ascending=False)
        df_filtrado = df_filtrado.drop("Urgencia_Order", axis=1)
    else:
        df_filtrado = df_filtrado.sort_values("País")
    
    # Mostrar resultados
    st.markdown(f"### 🎯 Resultados Filtrados: {len(df_filtrado)} de {len(df_resultados)}")
    
    for idx, row in df_filtrado.iterrows():
        with st.container():
            st.markdown("---")
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**🌍 {row['País']}**")
                st.markdown(f"**🔍 Keyword:** {row['Keyword']}")
                st.markdown(f"**📊 Anuncios:** {row['Anuncios']}")
            
            with col2:
                score_viral = row.get("Score_Viralidad", 0)
                mostrar_badge_viralidad(score_viral)
            
            with col3:
                urgencia = row.get("Urgencia", "BAJA")
                urgencia_data = {"urgencia": urgencia, "mensaje": f"Urgencia {urgencia}"}
                mostrar_badge_urgencia(urgencia_data)
            
            with col4:
                prioridad = row.get("Prioridad", "BAJA")
                score_data = {"prioridad": prioridad, "score_total": row.get("Score_Priorizacion", 0)}
                mostrar_badge_prioridad(score_data)
            
            # Botón para ver detalles
            if st.button(f"🔍 Ver Detalles #{idx+1}", key=f"detalles_{idx}"):
                with st.expander(f"Detalles completos - {row['Keyword']}", expanded=True):
                    mostrar_metricas_duplicados(row.get("Duplicados", {}))
                    if "Funnel" in row:
                        mostrar_funnel_analysis(row["Funnel"])
    
    # Resumen estadístico
    st.markdown("### 📈 Resumen Estadístico")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_score = df_filtrado["Score_Viralidad"].mean()
        st.metric("Score Promedio", f"{avg_score:.1f}")
    with col2:
        alta_prioridad = len(df_filtrado[df_filtrado["Prioridad"] == "ALTA"])
        st.metric("Alta Prioridad", alta_prioridad)
    with col3:
        alta_urgencia = len(df_filtrado[df_filtrado["Urgencia"] == "ALTA"])
        st.metric("Alta Urgencia", alta_urgencia)
    with col4:
        total_anuncios = df_filtrado["Anuncios"].sum()
        st.metric("Total Anuncios", f"{total_anuncios:,}")

# ==========================================
# 🔧 FUNCIONES DE UTILIDAD
# ==========================================

def mostrar_error(mensaje, error=None):
    """Función unificada para mostrar errores."""
    if error:
        logger.error(f"{mensaje}: {error}")
        st.error(f"{mensaje}: {error}")
    else:
        logger.error(mensaje)
        st.error(mensaje)

def get_driver_from_pool():
    """Obtiene un driver del pool o crea uno nuevo."""
    global DRIVER_POOL
    
    with DRIVER_LOCK:
        if DRIVER_POOL:
            return DRIVER_POOL.pop()
        else:
            return create_new_driver()

def return_driver_to_pool(driver):
    """Devuelve un driver al pool para reutilización."""
    global DRIVER_POOL
    
    with DRIVER_LOCK:
        if len(DRIVER_POOL) < MAX_DRIVERS:
            try:
                driver.delete_all_cookies()
                driver.execute_script("window.localStorage.clear();")
                driver.execute_script("window.sessionStorage.clear();")
                DRIVER_POOL.append(driver)
            except:
                try:
                    driver.quit()
                except:
                    pass
        else:
            try:
                driver.quit()
            except:
                pass

def create_new_driver():
    """Crea un nuevo driver con configuraciones optimizadas."""
    options = Options()
    
    # Configuraciones básicas
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-translate")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    
    # Anti-detección mejorado
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 2
    })
    
    # User Agent rotativo
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]
    options.add_argument(f"--user-agent={random.choice(user_agents)}")
    
    # Configuraciones adicionales
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-ipc-flooding-protection")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Scripts anti-detección
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        
        return driver
    except Exception as e:
        logger.error(f"Error creando driver: {e}")
        raise

def smart_delay():
    """Delay inteligente que varía según la actividad."""
    base_delay = random.uniform(1, 3)
    if len(rate_limiter.requests) > 20:
        base_delay *= 2
    time.sleep(base_delay)

def obtener_idioma_principal_pais(pais):
    """Obtiene el idioma principal de un país."""
    return PAIS_IDIOMA_PRINCIPAL.get(pais, 'english')

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
    if 'traducciones_cache' not in st.session_state:
        st.session_state.traducciones_cache = {}
    iso_code = LANG2ISO.get(idioma_destino, "en")
    translator = GoogleTranslator(source="es", target=iso_code)
    traducidas = []
    for palabra in palabras:
        cache_key = f"{iso_code}_{palabra}"
        if cache_key in st.session_state.traducciones_cache:
            traducidas.append(st.session_state.traducciones_cache[cache_key])
            continue
        try:
            traducida = translator.translate(palabra)
            traducidas.append(traducida)
            st.session_state.traducciones_cache[cache_key] = traducida
            time.sleep(CONFIG["delay_between_requests"])
        except Exception as e:
            logger.warning(f"Error traduciendo '{palabra}': {e}")
            st.warning(f"Error traduciendo '{palabra}': {e}")
            traducidas.append(palabra)
    return traducidas

def contar_anuncios(keyword, country):
    """Cuenta el número de anuncios activos en Facebook Ads Library para una keyword y país dados."""
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
        st.session_state.metricas_rendimiento['errores'] += 1
        return 0
    finally:
        driver.quit()
        time.sleep(CONFIG["delay_between_requests"])

# ==========================================
# 🎯 INTERFAZ PRINCIPAL STREAMLIT
# ==========================================

st.set_page_config(
    page_title="Mega Buscador PEV - Espionaje Viral",
    page_icon="🔥",
    layout="wide"
)

st.title("🔥 Mega Buscador PEV - Espionaje Viral")
st.markdown("### *Herramienta Avanzada de Espionaje Viral para Productos Digitales*")

# Sidebar con opciones
st.sidebar.title("🎛️ Configuración")

# Opciones de análisis viral
st.sidebar.markdown("### 🔥 Análisis Viral")
usar_analisis_viral = st.sidebar.checkbox("🚀 Análisis de duplicados", value=True)
mostrar_funnel = st.sidebar.checkbox("🔍 Análisis de funnel", value=True)
priorizar_paises = st.sidebar.checkbox("🎯 Priorización inteligente", value=True)

# Configuración de países
st.sidebar.markdown("### 🌍 Países Objetivo")
incluir_alta = st.sidebar.checkbox("🔥 Alta rentabilidad", value=True)
incluir_buena = st.sidebar.checkbox("⭐ Buena rentabilidad", value=True)
incluir_media = st.sidebar.checkbox("📝 Rentabilidad media", value=False)

# Selección de países
paises_selected = []
if incluir_alta:
    paises_selected.extend(PAISES_RENTABLES["alta_rentabilidad"])
if incluir_buena:
    paises_selected.extend(PAISES_RENTABLES["buena_rentabilidad"])
if incluir_media:
    paises_selected.extend(PAISES_RENTABLES["rentabilidad_media"])

# Interfaz principal
st.markdown("## 🔍 Análisis de Demanda con Espionaje Viral")

col1, col2 = st.columns(2)

with col1:
    keywords_input = st.text_area("Keywords manuales:", "ebook, curso, guía")
    busqueda_multilingue = st.checkbox('¿Buscar también en otros idiomas? (multilingüe)', value=False)

with col2:
    st.markdown("**Países seleccionados:**")
    st.write(f"Total: {len(paises_selected)} países")
    if paises_selected:
        st.write(", ".join([COUNTRY2NAME.get(p, p) for p in paises_selected[:5]]))
        if len(paises_selected) > 5:
            st.write(f"... y {len(paises_selected) - 5} más")

if st.button("🔥 Analizar con Espionaje Viral", type="primary"):
    if keywords_input and paises_selected:
        keywords = [kw.strip() for kw in keywords_input.split(",")]
        
        with st.spinner("🔥 Analizando con métricas de espionaje viral..."):
            resultados = []
            
            for pais in paises_selected:
                if busqueda_multilingue:
                    for idioma in LANGS.values():
                        keywords_traducidas = traducir_palabras(keywords, idioma)
                        for keyword in keywords_traducidas:
                            # Análisis básico
                            count = contar_anuncios(keyword, pais)
                            rentabilidad = analizar_rentabilidad(count)
                            
                            resultado = {
                                "País": f"{COUNTRY2NAME[pais]} ({pais})",
                                "Keyword": keyword,
                                "Anuncios": count,
                                "Estado": rentabilidad["estado"],
                                "Acción": rentabilidad["accion"]
                            }
                            
                            # Análisis viral si está habilitado
                            if usar_analisis_viral:
                                analisis_duplicados = analizar_duplicados_anuncios(keyword, pais)
                                urgencia = calcular_urgencia_lanzamiento(duplicados=analisis_duplicados["total_duplicados"])
                                
                                resultado["Duplicados"] = analisis_duplicados
                                resultado["Score_Viralidad"] = analisis_duplicados["score_viralidad"]
                                resultado["Urgencia"] = urgencia["urgencia"]
                                resultado["Mensaje_Urgencia"] = urgencia["mensaje"]
                            
                            # Score de priorización
                            if priorizar_paises:
                                score = calcular_score_priorizacion(
                                    anuncios_duplicados=resultado.get("Duplicados", {}).get("total_duplicados", 0),
                                    pais_objetivo=pais,
                                    facilidad_modelado="MEDIO",
                                    tiempo_activo=0
                                )
                                resultado["Score_Priorizacion"] = score["score_total"]
                                resultado["Prioridad"] = score["prioridad"]
                            
                            resultados.append(resultado)
                else:
                    idioma_pais = obtener_idioma_principal_pais(pais)
                    keywords_traducidas = traducir_palabras(keywords, idioma_pais)
                    for keyword in keywords_traducidas:
                        # Análisis básico
                        count = contar_anuncios(keyword, pais)
                        rentabilidad = analizar_rentabilidad(count)
                        
                        resultado = {
                            "País": f"{COUNTRY2NAME[pais]} ({pais})",
                            "Keyword": keyword,
                            "Anuncios": count,
                            "Estado": rentabilidad["estado"],
                            "Acción": rentabilidad["accion"]
                        }
                        
                        # Análisis viral si está habilitado
                        if usar_analisis_viral:
                            analisis_duplicados = analizar_duplicados_anuncios(keyword, pais)
                            urgencia = calcular_urgencia_lanzamiento(duplicados=analisis_duplicados["total_duplicados"])
                            
                            resultado["Duplicados"] = analisis_duplicados
                            resultado["Score_Viralidad"] = analisis_duplicados["score_viralidad"]
                            resultado["Urgencia"] = urgencia["urgencia"]
                            resultado["Mensaje_Urgencia"] = urgencia["mensaje"]
                        
                        # Score de priorización
                        if priorizar_paises:
                            score = calcular_score_priorizacion(
                                anuncios_duplicados=resultado.get("Duplicados", {}).get("total_duplicados", 0),
                                pais_objetivo=pais,
                                facilidad_modelado="MEDIO",
                                tiempo_activo=0
                            )
                            resultado["Score_Priorizacion"] = score["score_total"]
                            resultado["Prioridad"] = score["prioridad"]
                        
                        resultados.append(resultado)
            
            if resultados:
                df = pd.DataFrame(resultados)
                crear_tabla_resultados_viral(df)
                
                # Exportar resultados
                if st.button("📊 Exportar Resultados Completos"):
                    df.to_csv('resultados_espionaje_viral.csv', index=False)
                    st.success("Resultados exportados a 'resultados_espionaje_viral.csv'")
            else:
                st.error("No se obtuvieron resultados")
    else:
        st.error("Completa todos los campos")

# Footer
st.markdown("---")
st.markdown("### 🔥 Mega Buscador PEV - Espionaje Viral")
st.markdown("**Herramienta avanzada para detectar productos virales y oportunidades de copia rápida.**")

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
    options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver 