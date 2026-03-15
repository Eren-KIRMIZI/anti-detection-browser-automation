"""
StealthBrowser
──────────────
undetected-chromedriver + selenium-stealth üstüne kurulu,
fingerprint randomizasyonu ve proxy desteği olan browser engine.

ÖNEMLI: undetected-chromedriver, excludeSwitches ve useAutomationExtension
seçeneklerini kendi yönetir. Bunları add_experimental_option ile eklemek
"invalid argument: unrecognized chrome option" hatasına yol açar.
"""

import time
import random
import contextlib
from typing import Optional

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth

from config.settings import settings
from backend.core.fingerprint import Fingerprint, generate_fingerprint
from backend.utils.proxy_manager import proxy_manager
from backend.utils.logger import log


class StealthBrowser:
    """
    Kullanım (context manager):

        with StealthBrowser() as browser:
            browser.go("https://example.com")
            html = browser.page_source()
    """

    def __init__(
        self,
        fingerprint: Optional[Fingerprint] = None,
        proxy: Optional[str] = None,
        headless: Optional[bool] = None,
    ):
        self.fp = fingerprint or generate_fingerprint()
        self.proxy = proxy or (proxy_manager.get() if settings.proxy_enabled else None)
        self.headless = headless if headless is not None else settings.chrome_headless
        self.driver: Optional[uc.Chrome] = None

    # ── Başlat / Kapat ───────────────────────────────────────────────────────

    def start(self) -> "StealthBrowser":
        options = self._build_options()
        # headless'ı constructor'a ver — options içinde --headless eklemek
        # ile aynı anda kullanılırsa çakışır.
        self.driver = uc.Chrome(
            options=options,
            use_subprocess=True,
            headless=self.headless,
        )
        self._apply_stealth()
        self._patch_js()
        log.info(f"Browser başlatıldı | UA: {self.fp.user_agent[:60]}...")
        return self

    def quit(self):
        if self.driver:
            with contextlib.suppress(Exception):
                self.driver.quit()
            self.driver = None
            log.info("Browser kapatıldı.")

    def __enter__(self):
        return self.start()

    def __exit__(self, *_):
        self.quit()

    # ── Chrome Options ────────────────────────────────────────────────────────

    def _build_options(self) -> uc.ChromeOptions:
        opts = uc.ChromeOptions()

        # headless'ı burada EKLEME — uc.Chrome(headless=...) constructor
        # parametresiyle geçiyoruz. İkisini birden kullanmak çakışır.

        opts.add_argument(f"--window-size={self.fp.width},{self.fp.height}")
        opts.add_argument(f"--lang={self.fp.accept_language}")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-infobars")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-first-run")
        opts.add_argument("--no-service-autorun")
        opts.add_argument("--password-store=basic")
        opts.add_argument("--disable-popup-blocking")

        # WebRTC gerçek IP sızıntısını engelle
        opts.add_argument("--force-webrtc-ip-handling-policy=disable_non_proxied_udp")

        if self.proxy:
            opts.add_argument(f"--proxy-server={self.proxy}")
            log.debug(f"Proxy eklendi: {self.proxy}")

        # !! add_experimental_option KULLANMA !!
        # excludeSwitches / useAutomationExtension'ı undetected-chromedriver
        # kendi yönetir. Elle eklemek şu hataya yol açar:
        #   "invalid argument: unrecognized chrome option: excludeSwitches"

        return opts

    # ── Stealth + JS Patch ────────────────────────────────────────────────────

    def _apply_stealth(self):
        stealth(
            self.driver,
            user_agent=self.fp.user_agent,
            languages=self.fp.languages,
            vendor="Google Inc.",
            platform=self.fp.platform,
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    def _patch_js(self):
        """navigator ve screen özelliklerini CDP ile override et."""
        js = f"""
        Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
        Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {self.fp.hardware_concurrency}}});
        Object.defineProperty(navigator, 'deviceMemory', {{get: () => {self.fp.device_memory}}});
        Object.defineProperty(navigator, 'platform', {{get: () => '{self.fp.platform}'}});
        Object.defineProperty(navigator, 'languages', {{get: () => {self.fp.languages}}});
        Object.defineProperty(screen, 'width',  {{get: () => {self.fp.width}}});
        Object.defineProperty(screen, 'height', {{get: () => {self.fp.height}}});
        Object.defineProperty(screen, 'colorDepth', {{get: () => {self.fp.color_depth}}});
        """
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument", {"source": js}
        )
        log.debug("JS patch uygulandı.")

    # ── Navigasyon ────────────────────────────────────────────────────────────

    def go(self, url: str, wait: float = 1.5):
        self.driver.get(url)
        time.sleep(wait)
        log.info(f"Navigasyon: {url}")

    def wait_for(self, css: str, timeout: int = 15):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css))
        )

    def page_source(self) -> str:
        return self.driver.page_source

    def screenshot(self, path: str = "data/screenshot.png") -> str:
        self.driver.save_screenshot(path)
        log.info(f"Screenshot kaydedildi: {path}")
        return path

    def current_url(self) -> str:
        return self.driver.current_url

    def title(self) -> str:
        return self.driver.title

    # ── İnsan Davranışı ───────────────────────────────────────────────────────

    def human_scroll(self, times: int = 3, delay: float = 0.6):
        for _ in range(times):
            amount = random.randint(200, 600)
            self.driver.execute_script(f"window.scrollBy(0, {amount});")
            time.sleep(delay + random.uniform(0, 0.4))
        log.debug(f"human_scroll: {times}x")

    def human_move(self, element):
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.move_by_offset(random.randint(-5, 5), random.randint(-5, 5))
        actions.perform()
        time.sleep(random.uniform(0.1, 0.3))

    def human_click(self, element):
        self.human_move(element)
        element.click()
        time.sleep(random.uniform(0.3, 0.8))

    def human_type(self, element, text: str, wpm: int = 180):
        delay_per_char = 60 / (wpm * 5)
        for char in text:
            element.send_keys(char)
            time.sleep(delay_per_char + random.uniform(0, delay_per_char * 0.5))

    def random_delay(self, min_s: float = 1.0, max_s: float = 3.0):
        time.sleep(random.uniform(min_s, max_s))

    # ── Fingerprint Bilgisi ───────────────────────────────────────────────────

    def fingerprint_info(self) -> dict:
        return {
            "user_agent": self.fp.user_agent,
            "languages": self.fp.languages,
            "timezone": self.fp.timezone,
            "resolution": f"{self.fp.width}x{self.fp.height}",
            "platform": self.fp.platform,
            "hardware_concurrency": self.fp.hardware_concurrency,
            "device_memory": self.fp.device_memory,
            "proxy": self.proxy or "none",
        }
