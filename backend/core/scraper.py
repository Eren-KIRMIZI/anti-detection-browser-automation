"""
ScraperService
──────────────
StealthBrowser üstüne kurulu yüksek seviyeli scraping servisi.
"""

import time
from typing import Optional
from backend.core.browser import StealthBrowser
from backend.core.fingerprint import generate_fingerprint
from backend.utils.logger import log


class ScraperService:

    def scrape(
        self,
        url: str,
        wait_css: Optional[str] = None,
        scroll: bool = False,
        headless: bool = True,
        screenshot: bool = False,
        screenshot_path: str = "data/screenshot.png",
    ) -> dict:
        """
        Tek sayfa scrape et.

        Döner:
            {
                "url": str,
                "title": str,
                "html": str,
                "screenshot": str | None,
                "fingerprint": dict,
                "elapsed": float,
            }
        """
        t0 = time.time()
        fp = generate_fingerprint()

        with StealthBrowser(fingerprint=fp, headless=headless) as browser:
            browser.go(url)

            if wait_css:
                try:
                    browser.wait_for(wait_css)
                except Exception:
                    log.warning(f"wait_css elementi bulunamadı: {wait_css}")

            if scroll:
                browser.human_scroll(times=4)

            browser.random_delay(1.0, 2.5)

            result = {
                "url": browser.current_url(),
                "title": browser.title(),
                "html": browser.page_source(),
                "screenshot": None,
                "fingerprint": browser.fingerprint_info(),
                "elapsed": round(time.time() - t0, 2),
            }

            if screenshot:
                path = browser.screenshot(screenshot_path)
                result["screenshot"] = path

        log.info(f"Scrape tamamlandı: {url} ({result['elapsed']}s)")
        return result

    def multi_scrape(self, urls: list[str], **kwargs) -> list[dict]:
        """Birden fazla URL'yi sırayla scrape et."""
        results = []
        for url in urls:
            try:
                r = self.scrape(url, **kwargs)
                results.append({"status": "ok", **r})
            except Exception as e:
                log.error(f"Scrape hatası [{url}]: {e}")
                results.append({"status": "error", "url": url, "error": str(e)})
        return results

    def check_bot_detection(self, url: str = "https://bot.sannysoft.com") -> dict:
        """
        Bot tespit sayfasını ziyaret ederek sonuçları döndür.
        Döndürdüğü HTML'den manuel analiz yapılabilir.
        """
        return self.scrape(url, scroll=False, headless=False, screenshot=True, screenshot_path="data/bot_check.png")


scraper = ScraperService()
