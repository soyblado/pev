import os
import asyncio
import nodriver as uc
from dotenv import load_dotenv

# --- Carga las variables de entorno ---
load_dotenv()
PROXY_USER = os.getenv('PROXY_USER')
PROXY_PASS = os.getenv('PROXY_PASS')
PROXY_HOST = os.getenv('PROXY_HOST')
PROXY_PORT = os.getenv('PROXY_PORT')

TARGET_URL = "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&q=libros%20de%20desarrollo%20personal&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_exact_phrase&media_type=all"

async def main():
    """Script de diagnóstico para descubrir los métodos del objeto 'page'."""
    print("--- INICIANDO SCRIPT DE DIAGNÓSTICO ---")
    proxy_server = f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}'
    browser_args = [f'--proxy-server={proxy_server}']
    
    try:
        async with await uc.start(browser_args=browser_args) as browser:
            page = await browser.get(TARGET_URL)
            print("Página cargada. Esperando 5 segundos...")
            await asyncio.sleep(5)

            print("\n--- MÉTODOS Y ATRIBUTOS DISPONIBLES PARA EL OBJETO 'page' ---")
            # Usamos la función dir() de Python para obtener una lista de todo lo que
            # el objeto 'page' puede hacer.
            print(dir(page))
            print("\n--- DIAGNÓSTICO FINALIZADO ---")

    except Exception as e:
        print(f"Ocurrió un error general en el diagnóstico: {e}")

if __name__ == '__main__':
    uc.loop().run_until_complete(main())