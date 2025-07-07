# Se necesita instalar la librería de Selenium:
# pip install selenium

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote # Importante para codificar las palabras clave en la URL
import time
import re

# --- CONFIGURACIÓN Y DATOS DE ENTRADA DEL USUARIO ---
print("--- Búsqueda de E-books por URL Directa (Método Definitivo) ---")

while True:
    try:
        MINIMUM_ADS_TO_BE_WINNER = int(input("Introduce el número MÍNIMO de anuncios para considerar un ebook como 'ganador': "))
        if MINIMUM_ADS_TO_BE_WINNER > 0:
            break
    except ValueError:
        print("Entrada no válida. Por favor, introduce un número entero.")

# --- PARÁMETROS DE BÚSQUEDA ---
BASE_URL = 'https://www.facebook.com/ads/library/'

# Países objetivo para la búsqueda.
TARGET_COUNTRIES = {
    'CO': 'Colombia',
    'US': 'Estados Unidos',
    'FR': 'Francia',
    'BR': 'Brasil'
}

# Palabras clave en los 4 idiomas
ALL_KEYWORDS = list(set([
    'libro electronico', 'guia digital', 'descarga ahora', 'ebook', 
    'digital guide', 'download now', 'get your copy', 
    'livre numérique', 'guide numérique', 'téléchargez maintenant', 
    'livro digital', 'guia digital', 'baixe agora'
]))

# El único selector que necesitamos: el que muestra el número de resultados.
RESULTS_TEXT_XPATH = '//div[contains(text(), " resultado") or contains(text(), " result")]'


def find_winners_by_url(driver, country_code, country_name, keyword):
    """
    Construye una URL de búsqueda, navega a ella y extrae el número de anuncios.
    """
    # Codificar la palabra clave para que funcione en una URL (ej: "libro digital" -> "libro%20digital")
    encoded_keyword = quote(keyword)
    
    # Construir la URL de búsqueda directa
    search_url = f"{BASE_URL}?active_status=all&ad_type=all&country={country_code}&q={encoded_keyword}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_exact_phrase"
    
    print(f"Navegando a la búsqueda en {country_name} para: '{keyword}'")
    driver.get(search_url)

    try:
        # Esperar a que el texto con los resultados aparezca en la página
        results_text_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, RESULTS_TEXT_XPATH))
        )
        results_text = results_text_element.text
        
        # Extraer el número del texto "Cerca de 1,700 resultados" -> 1700
        found_numbers = re.findall(r'[\d,.]+', results_text)
        if found_numbers:
            num_ads = int(re.sub(r'[,.]', '', found_numbers[0]))
            return num_ads
        else:
            return 0
            
    except Exception:
        # Si no se encuentra el elemento de resultados, asumimos que hay 0 anuncios.
        print(f"No se encontraron resultados para '{keyword}' en {country_name}.")
        return 0


def main():
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    print("\nIniciando búsqueda general de ebooks en países clave...")

    # Bucle principal que itera sobre cada país y cada palabra clave
    for country_code, country_name in TARGET_COUNTRIES.items():
        print(f"\n{'='*30}\nAnalizando: {country_name.upper()}\n{'='*30}")
        for keyword in ALL_KEYWORDS:
            
            num_ads = find_winners_by_url(driver, country_code, country_name, keyword)
            
            if num_ads >= MINIMUM_ADS_TO_BE_WINNER:
                print("\n" + "!"*40)
                print(f"¡ÉXITO en {country_name.upper()}!")
                print(f"La palabra clave '{keyword}' es popular.")
                print(f"Anuncios encontrados: {num_ads} (Mínimo requerido: {MINIMUM_ADS_TO_BE_WINNER})")
                print(f"Puedes revisar los resultados en: {driver.current_url}")
                print("!"*40 + "\n")
            else:
                # Opcional: imprimir si no se alcanzan los resultados para mantener informado
                # print(f"-> {num_ads} anuncios para '{keyword}'. No cumple el mínimo.")
                pass
            
            time.sleep(2) # Pequeña pausa para no saturar de peticiones

    print("\nBúsqueda finalizada en todos los países objetivo.")
    driver.quit()

if __name__ == "__main__":
    main()