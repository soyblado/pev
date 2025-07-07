from playwright.async_api import async_playwright

async def fetch_hotmart(USER, PASS):
    # Lanzarlo *no* en modo headless y con un poco de retraso
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False, slow_mo=100)
    page = await browser.new_page()

    await page.goto("https://app-vlc.hotmart.com/login", timeout=60000)
    # Aquí inspecciona manualmente en la ventana que abrió si el selector coincide
    await page.wait_for_selector('input[name="email"]', timeout=60000)
    await page.fill('input[name="email"]', USER)
    await page.fill('input[name="password"]', PASS)
    await page.click('button[type="submit"]')

    # Esperar a que el dashboard aparezca
    await page.wait_for_selector("nav[aria-label='Dashboard']", timeout=60000)
    print("✅ Login OK, estás en tu dashboard")

    # ... haz más cosas aquí, por ejemplo capturar anuncios ...
    # Por ahora solo lo cerramos al final:
    await browser.close()
    await playwright.stop()

if __name__ == "__main__":
    import asyncio, os
    from dotenv import load_dotenv

    load_dotenv()
    USER = os.getenv("HOTMART_USER")
    PASS = os.getenv("HOTMART_PASS")
    asyncio.run(fetch_hotmart(USER, PASS))
