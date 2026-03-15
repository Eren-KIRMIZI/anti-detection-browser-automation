# 🦊 Stealth Engine

Anti-detection browser otomasyon projesi.
**Stack:** FastAPI + undetected-chromedriver + Selenium Stealth + Cyberpunk Dashboard

---

## 📁 Proje Yapısı

```
stealth-engine/
├── main.py                         # FastAPI entrypoint
├── requirements.txt
├── .env                            # Konfigürasyon
│
├── config/
│   └── settings.py                 # Pydantic Settings
│
├── backend/
│   ├── core/
│   │   ├── browser.py              # StealthBrowser ana sınıfı
│   │   ├── fingerprint.py          # Fingerprint randomizer
│   │   └── scraper.py              # ScraperService
│   ├── api/
│   │   └── routes.py               # FastAPI endpoint'leri
│   └── utils/
│       ├── logger.py               # Loguru logger
│       └── proxy_manager.py        # Proxy yönetimi
│
├── frontend/
│   └── index.html                  # Cyberpunk dashboard (aynı porttan serve edilir)
│
├── data/
│   └── proxies/
│       └── proxies.txt             # Proxy listesi
│
└── logs/
    └── stealth.log                 # Otomatik oluşur
```

---

## 🚀 Kurulum

```bash
# 1. Sanal ortam oluştur
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Bağımlılıkları kur
pip install -r requirements.txt

# 3. Chrome yüklü olduğundan emin ol
# undetected-chromedriver Chrome versiyonunu otomatik eşler

# 4. .env dosyasını düzenle (opsiyonel)
nano .env
```

---

## ▶️ Çalıştır

```bash
# Geliştirme (hot-reload ile)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Prodüksiyon
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
# Not: workers=1 önemli — undetected-chromedriver multi-process'te sorun çıkarabilir
```

Tarayıcıda aç:
- **Dashboard:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 📡 API Endpoint'leri

### GET `/api/v1/health`
API ve proxy durumunu döndürür.

### GET `/api/v1/fingerprint/new`
Rastgele bir fingerprint üretir.
```json
{
  "user_agent": "Mozilla/5.0 ...",
  "languages": ["tr-TR", "tr", "en-US"],
  "timezone": "Europe/Istanbul",
  "resolution": "1920x1080",
  "platform": "Win32",
  "hardware_concurrency": 8,
  "device_memory": 16
}
```

### POST `/api/v1/scrape`
```json
{
  "url": "https://example.com",
  "wait_css": "body",
  "scroll": false,
  "headless": true,
  "screenshot": false
}
```

### POST `/api/v1/scrape/multi`
```json
{
  "urls": ["https://site1.com", "https://site2.com"],
  "headless": true,
  "scroll": false
}
```

### POST `/api/v1/bot-check`
```json
{
  "url": "https://bot.sannysoft.com"
}
```

---

## 🔧 Proxy Ayarı

`data/proxies/proxies.txt` dosyasına ekle:
```
http://user:pass@host:port
socks5://host:port
```

`.env` içinde aktif et:
```
PROXY_ENABLED=true
PROXY_ROTATION=true
```

---

## 🐍 Python'da Doğrudan Kullanım

```python
from backend.core.browser import StealthBrowser
from backend.core.scraper import scraper

# Context manager ile
with StealthBrowser(headless=True) as browser:
    browser.go("https://example.com")
    browser.human_scroll(times=3)
    print(browser.title())
    print(browser.page_source()[:500])

# Scraper servisi ile
result = scraper.scrape(
    url="https://httpbin.org/headers",
    scroll=True,
    headless=True,
    screenshot=True,
)
print(result["title"])
print(result["fingerprint"])
```

---

## ⚠️ Önemli Notlar

- **Chrome** yüklü olmalı. undetected-chromedriver ChromeDriver'ı otomatik indirir.
- `workers=1` kullan — her worker ayrı browser instance açar, multi-worker'da Chrome crash verebilir.
- Proxy listesi boşsa proxy kullanılmaz, doğrudan bağlantı yapılır.
- `CHROME_HEADLESS=false` ile Chrome penceresini görebilirsin (debug için).
- Bot tespit testi (`/api/v1/bot-check`) headful modda çalışır, Chrome penceresi açar.
