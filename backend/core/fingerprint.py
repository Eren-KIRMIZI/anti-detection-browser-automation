import random
from dataclasses import dataclass

# ── Desktop-only Chrome User Agent havuzu ────────────────────────────────────
# fake_useragent.chrome bazen Android/Mobile UA döndürüyor.
# PHANTOM_UA testini geçmek için Windows/Mac masaüstü UA'ları kullanıyoruz.
DESKTOP_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

LANGUAGES = [
    ["tr-TR", "tr", "en-US", "en"],
    ["en-US", "en"],
    ["de-DE", "de", "en-US", "en"],
    ["fr-FR", "fr", "en-US", "en"],
    ["es-ES", "es", "en-US", "en"],
]

TIMEZONES = [
    "Europe/Istanbul",
    "Europe/Berlin",
    "Europe/London",
    "America/New_York",
    "America/Los_Angeles",
    "Asia/Tokyo",
    "Asia/Singapore",
]

# Sadece masaüstü çözünürlükleri
RESOLUTIONS = [
    (1920, 1080),
    (2560, 1440),
    (1440, 900),
    (1536, 864),
    (1280, 800),
    (1680, 1050),
    (2560, 1080),
]

# UA'ya göre platform eşleştirmesi için
PLATFORM_MAP = {
    "Windows": "Win32",
    "Macintosh": "MacIntel",
    "X11": "Linux x86_64",
}

HW_CONCURRENCY = [4, 6, 8, 12, 16]
DEVICE_MEMORY  = [4, 8, 16]


@dataclass
class Fingerprint:
    user_agent: str
    languages: list[str]
    timezone: str
    width: int
    height: int
    platform: str
    hardware_concurrency: int
    device_memory: int
    color_depth: int = 24

    @property
    def accept_language(self) -> str:
        return ",".join(self.languages)


def _platform_from_ua(ua: str) -> str:
    """UA stringinden platform çıkar — tutarsız kombinasyon olmasın."""
    for key, val in PLATFORM_MAP.items():
        if key in ua:
            return val
    return "Win32"


def generate_fingerprint() -> Fingerprint:
    ua = random.choice(DESKTOP_UAS)
    w, h = random.choice(RESOLUTIONS)
    return Fingerprint(
        user_agent=ua,
        languages=random.choice(LANGUAGES),
        timezone=random.choice(TIMEZONES),
        width=w,
        height=h,
        platform=_platform_from_ua(ua),
        hardware_concurrency=random.choice(HW_CONCURRENCY),
        device_memory=random.choice(DEVICE_MEMORY),
    )
