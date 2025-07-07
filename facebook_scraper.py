# scrapers/facebook_ui_scraper.py

import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from playwright.async_api import async_playwright

async def fetch_ads_ui(search_term: str, country: str = "US", pages: int = 3):
    URL = "https://www.facebook.com/ads/library/"
    print("→ Lanzando navegador…")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=[
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

        print(f"→ Navegando a {URL}")
        await page.goto(URL, wait_until="networkidle")

        print(f"→ Esperando combobox de búsqueda…")
        # Este es el verdadero input de anuncios
        combo = page.locator('input[role="combobox"][aria-label*="Buscar"]')
        await combo.wait_for(state="visible", timeout=15000)

        print(f"→ Rellenando con «{search_term}»")
        await combo.fill(search_term)
        await combo.press("Enter")
        await page.wait_for_load_state("networkidle")

        ads = []
        for i in range(pages):
            print(f"→ Extrayendo página {i+1}/{pages}")
            await asyncio.sleep(2)
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select('[data-testid="ad-card"]')
            print(f"   • {len(cards)} tarjetas encontradas")
            for card in cards:
                texto = card.get_text(" ").strip()
                img = card.select_one("img")
                ads.append({
                    "texto_copy": texto[:200],
                    "url_imagen": img["src"] if img else None,
                    "pais": country,
                    "fecha": datetime.now().isoformat()
                })

            # siguiente página
            btn = page.locator('[aria-label="Siguiente"], button:has-text("Siguiente")')
            if await btn.count() and await btn.is_enabled():
                print("   → Clic en Siguiente")
                await btn.click()
                await page.wait_for_load_state("networkidle")
            else:
                print("   → No hay Siguiente, fin.")
                break

        print("→ Cerrando navegador")
        await browser.close()
    return ads

if __name__ == "__main__":
    resultados = asyncio.run(fetch_ads_ui(
        search_term="ebook belleza",
        country="ES",
        pages=3
    ))
    print(f"\nSe encontraron {len(resultados)} anuncios.")
    for ad in resultados[:5]:
        print(ad)
