import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os

# Carga variables de entorno
load_dotenv()
HOTMART_USER = os.getenv("HOTMART_USER")
HOTMART_PASS = os.getenv("HOTMART_PASS")
if not HOTMART_USER or not HOTMART_PASS:
    raise RuntimeError("🛑 HOTMART_USER y/o HOTMART_PASS no definidos en .env")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        # 1) Navega al login
        await page.goto("https://app-vlc.hotmart.com/login", wait_until="networkidle")
        # 2) Espera y rellena email
        await page.wait_for_selector('input[type="email"]', timeout=60000)
        await page.fill('input[type="email"]', HOTMART_USER)
        # 3) Espera y rellena contraseña
        await page.wait_for_selector('input[type="password"]', timeout=60000)
        await page.fill('input[type="password"]', HOTMART_PASS)
        # 4) Envía el formulario y espera carga
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')
        # 5) Verifica dashboard
        if await page.query_selector('nav[aria-label*="Dashboard"]'):
            print("✅ Login exitoso en Hotmart")
        else:
            print("❌ No detecté el Dashboard, login falló")
        # Aquí comienza tu scraping (ejemplo)
        # ...
        # await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
