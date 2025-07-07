# Se necesita instalar la librería de Selenium:
# pip install selenium

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
import time
import re

# =======================================================================
# ¡AQUÍ ESTÁ LA CLAVE!
# Edita esta lista con los nombres EXACTOS de las Páginas de Facebook
# o los dominios web (ej: "dominio.com") de los ebooks ganadores
# que tienes en tus PDFs o que has encontrado.
# He puesto los de tu captura anterior como ejemplo.
# =======================================================================
TARGET_ADVERTISERS = [
    "Infinito Desarrollo Personal", # Nombre de la Página de Facebook
    "Soy Sandra Milena",            # Nombre de la Página de Facebook
    "Equipo Black Box",             # Nombre de la Página de Facebook
    # "ejemplo.com",                # Ejemplo si tuvieras un dominio
    # "Otro Anunciante Famoso"
]
# =======================================================================


# --- CONFIGURACIÓN Y DATOS DE ENTRADA DEL USUARIO ---
print("--- Análisis Específico de Anunciantes (Método Forense) ---")

# --- PARÁMETROS DE BÚSQUEDA ---
BASE_URL = 'https://www.facebook.com/ads/library/'
TARGET_COUNTRIES = {
    'CO': 'Colombia',
    'US': 'Estados Unidos',
    'FR': 'Francia',
    'BR': 'Brasil',
    'ES': 'España', # Añadido España, un mercado grande de habla hispana
    'MX': 'México'  # Añadido México, otro mercado clave
}
RESULTS_TEXT_XPATH = '//div[contains(text(), " resultado") or contains(text(), " result")]'


def analyze_advertiser(driver, country_code, country_name, advertiser_name):
    """
    Busca un anunciante o dominio específico y devuelve el número de anuncios.
    """
    encoded_advertiser = quote(advertiser_name)
    search_url = f"{BASE_URL}?active_status=all&ad_type=all&country={country_code}&q={encoded_advertiser}&search_type=keyword_exact_phrase"
    
    print(f"Investigando en {country_name} al anunciante: '{advertiser_name}'")
    driver.get(search_url)

    try:
        results_text_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, RESULTS_TEXT_XPATH))
        )
        results_text = results_text_element.text
        found_numbers = re.findall(r'[\d,.]+', results_text)
        if found_numbers:
            num_ads = int(re.sub(r'[,.]', '', found_numbers[0]))
            return num_ads
        else:
            return 0
    except Exception:
        print(f"-> No se encontraron resultados para '{advertiser_name}' en {country_name}.")
        return 0


def main():
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    print("\nIniciando análisis forense de anunciantes conocidos...")
    total_winners = 0

    for advertiser in TARGET_ADVERTISERS:
        print(f"\n{'='*40}\nAnalizando al competidor: {advertiser.upper()}\n{'='*40}")
        found_as_winner = False
        for country_code, country_name in TARGET_COUNTRIES.items():
            
            num_ads = analyze_advertiser(driver, country_code, country_name, advertiser)
            
            # Para este análisis, cualquier número de anuncios es interesante.
            if num_ads > 0:
                print(f"  ¡ENCONTRADO! '{advertiser}' tiene {num_ads} anuncios activos en {country_name}.")
                found_as_winner = True
                total_winners += 1
            
            time.sleep(2)
        
        if not found_as_winner:
            print(f"-> El anunciante '{advertiser}' no tiene anuncios activos detectables en los países analizados.")

    print(f"\nAnálisis finalizado. Se encontraron {total_winners} casos de anuncios activos.")
    driver.quit()

if __name__ == "__main__":
    main()