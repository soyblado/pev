import os
import asyncio
import nodriver as uc
from dotenv import load_dotenv
import random

# --- Carga las variables de entorno desde el archivo .env ---
load_dotenv()
PROXY_USER = os.getenv('PROXY_USER')
PROXY_PASS = os.getenv('PROXY_PASS')
PROXY_HOST = os.getenv('PROXY_HOST')
PROXY_PORT = os.getenv('PROXY_PORT')

# --- CONFIGURACIÓN DEL SCRAPER ---
# 1. El término que queremos buscar en la Biblioteca de Anuncios
SEARCH_TERM = "libros de desarrollo personal"
# 2. La URL de la Biblioteca de Anuncios
TARGET_URL = "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&q=libros%20de%20desarrollo%20personal&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_exact_phrase&media_type=all"

async def main():
    """Función principal del scraper para la Biblioteca de Anuncios de Facebook."""
    print(f"Iniciando scraper para buscar: '{SEARCH_TERM}'")

    # --- Configuración del Proxy ---
    proxy_server = None
    if PROXY_USER and PROXY_PASS and PROXY_HOST and PROXY_PORT:
        proxy_server = f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}'
        print(f"Usando proxy: {PROXY_HOST}")
    else:
        print("Proxy no configurado. Usando IP local.")

    browser_args = []
    if proxy_server:
        browser_args.append(f'--proxy-server={proxy_server}')

    # --- Inicio y Gestión Automática del Navegador ---
    print("Iniciando navegador...")
    try:
        async with await uc.start(browser_args=browser_args) as browser:
            # Creamos una nueva pestaña (página)
            page = await browser.get(TARGET_URL)
            print(f"Navegando a: {TARGET_URL}")
            
            # --- INTERACCIÓN CON LA PÁGINA ---
            # Facebook es lento para cargar. Damos tiempo suficiente.
            print("Esperando 10 segundos a que la página cargue completamente...")
            await asyncio.sleep(10)

            # ACEPTAR COOKIES: Buscamos el botón de aceptar cookies.
            # Los selectores de Facebook son complejos. Usamos atributos como 'data-testid'.
            # Si la página de cookies no aparece, este bloque dará un error y continuará.
            try:
                print("Buscando el botón de aceptar cookies...")
                # Este selector busca un botón que contiene otro elemento con el texto "Permitir todas las cookies"
                cookie_button_selector = "//div[contains(., 'Permitir todas las cookies') and @role='button']"
                cookie_button = await page.find(cookie_button_selector, by='xpath')
                await cookie_button.click()
                print("Cookies aceptadas. Esperando 2 segundos...")
                await asyncio.sleep(2)
            except Exception as e:
                print("No se encontró el banner de cookies o ya fue aceptado. Continuando...")

            # --- EXTRACCIÓN DE DATOS ---
            print("Buscando los contenedores de los anuncios...")
            # Este selector es un ejemplo. Facebook lo cambia a menudo.
            # Busca divs que parecen ser los contenedores principales de los anuncios.
            # ADVERTENCIA: Este selector es FRÁGIL y probablemente necesite ser actualizado.
            ad_container_selector = "div.x1yztbdb.x1n2onr6.xh8yej3.x1ja2u2z"

            # Esperamos a que al menos un anuncio aparezca en la página
            await page.wait_for(ad_container_selector, timeout=20)
            print("¡Contenedores de anuncios encontrados!")

            # Obtenemos todos los elementos que coinciden con el selector
            ad_elements = await page.select_all(ad_container_selector)
            print(f"Se encontraron {len(ad_elements)} anuncios en la primera carga.")
            
            print("\n--- INICIO DE EXTRACCIÓN DE ANUNCIOS ---\n")
            
            count = 0
            for ad in ad_elements:
                if count >= 5: # Limitamos a los primeros 5 anuncios para esta prueba
                    break
                try:
                    # Intentamos obtener el texto completo del anuncio.
                    ad_text = await ad.text()
                    print(f"--- ANUNCIO #{count + 1} ---")
                    # Imprimimos solo los primeros 400 caracteres para no llenar la consola
                    print(ad_text[:400] + "...")
                    print("\n" + "="*50 + "\n")
                    count += 1
                    # Pequeña pausa aleatoria para simular comportamiento humano
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                except Exception as e:
                    print(f"No se pudo extraer el texto de un anuncio: {e}")

        print("\nProceso finalizado con éxito.")

    except Exception as e:
        print(f"Ocurrió un error general durante la ejecución: {e}")
        # Guardar captura de pantalla si ocurre un error inesperado
        if 'page' in locals() and page:
            await page.save_screenshot('error_general_screenshot.png')
            print("Se ha guardado una captura del error en 'error_general_screenshot.png'")
    
if __name__ == '__main__':
    uc.loop().run_until_complete(main())