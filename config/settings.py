from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_secret_key: str = "change-me"
    debug: bool = True

    # Browser
    chrome_headless: bool = False
    chrome_window_w: int = 1920
    chrome_window_h: int = 1080
    page_load_timeout: int = 30
    implicit_wait: int = 10

    # Proxy
    proxy_enabled: bool = False
    proxy_rotation: bool = True
    proxy_file: str = "data/proxies/proxies.txt"

    # Fingerprint
    randomize_ua: bool = True
    randomize_lang: bool = True
    randomize_timezone: bool = True
    default_locale: str = "tr-TR"
    default_timezone: str = "Europe/Istanbul"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/stealth.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
