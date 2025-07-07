# scrapers/facebook_ui_scraper.py

import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from playwright.async_api import async_playwright

async def fetch_ads_ui(search_term: str, country: str = "US", pages: int = 5):
    url = "https://www.facebook.com/ads/library/"
    ads = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled"
        ])
        context = await browser.new_context(
            locale="es-ES",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        )
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle")

        # Llenar búsqueda
        await page.fill('input[placeholder*="Buscar"]', search_term)
        await page.press('input[placeholder*="Buscar"]', 'Enter')
        await page.wait_for_load_state("networkidle")

        for _ in range(pages):
            await asyncio.sleep(2)
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select('[data-testid="ad-card"]')
            for card in cards:
                texto = card.get_text(separator=" ").strip()
                img = card.select_one("img")
                ads.append({
                    "texto_copy": texto[:200],
                    "url_imagen": img["src"] if img else None,
                    "pais": country,
                    "fecha": datetime.now().isoformat()
                })
            # Pasar a la siguiente página
            nxt = await page.query_selector('[aria-label="Siguiente"]')
            if nxt:
                await nxt.click()
                await page.wait_for_load_state("networkidle")
            else:
                break

        await browser.close()
    return ads

if __name__ == "__main__":
    resultados = asyncio.run(fetch_ads_ui(
        "ebook belleza", country="ES", pages=3
    ))
    print(f"Se encontraron {len(resultados)} anuncios (UI scraping).")
    for ad in resultados[:5]:
        print(ad)
