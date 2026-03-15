# Stealth Engine

Stealth Engine, web sitelerinin bot tespit sistemlerini atlatmak için geliştirilmiş bir tarayıcı otomasyon altyapısıdır. Standart otomasyon araçlarının JavaScript katmanında yaptığı kimlik gizleme işlemlerini, tarayıcının C++ implementasyon katmanında gerçekleştirir. Bu sayede siteler JS üzerinden kontrol yaptığında bile sistem gerçek bir kullanıcı olarak görünür.

https://github.com/user-attachments/assets/edeada47-e30e-4f76-87c5-f10d10ea664a

Proje; bir FastAPI backend, Selenium tabanlı tarayıcı motoru ve bunları tek arayüzden yöneten bir dashboard'dan oluşur.

---

## Ne Yapar

Bir siteye otomatik araçla girildiğinde tespit sistemleri onlarca farklı sinyali analiz eder. Stealth Engine bu sinyallerin tamamını maskeler:

- `navigator.webdriver` alanı tanımsız bırakılarak Selenium'un en belirgin izi kaldırılır
- İşletim sistemi, cihaz modeli, CPU çekirdek sayısı, RAM ve ekran çözünürlüğü rastgele ama tutarlı değerlerle doldurulur
- WebRTC üzerinden gerçek IP adresinin sızması UDP politikası zorunlu kılınarak engellenir
- Her oturumda gerçek bir Chrome sürümüne ait kullanıcı ajanı atanır
- Fare hareketleri, sayfa kaydırma ve klavye girişleri insan davranışını taklit edecek şekilde simüle edilir
- Proxy listesinden otomatik rotasyon yapılır; başarısız proxy'ler listeden çıkarılır

---

## Teknolojiler

| Katman | Teknoloji | Kullanim Amaci |
|---|---|---|
| Backend | FastAPI | REST API, endpoint yönetimi, CORS |
| Sunucu | uvicorn | ASGI sunucusu |
| Tarayici Motoru | undetected-chromedriver | C++ seviyesinde otomasyon izlerini kaldırır |
| Otomasyon | Selenium | Tarayıcı kontrolü ve element etkileşimi |
| Stealth | selenium-stealth | JS özelliklerini gerçek değerlerle doldurur |
| Fingerprint | fake-useragent | Güncel ve gerçek kullanıcı ajanı veritabanı |
| Konfigurasyon | pydantic-settings | .env tabanlı tip güvenli ayar yönetimi |
| Loglama | loguru | Renkli konsol çıktısı, dosya rotasyonu |
| Frontend | HTML / CSS / JS | Dashboard arayüzü, framework bağımlılığı yok |

---
## Proje Yapısı

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

## Kurulum

Python 3.11+ ve Google Chrome yüklü olmalıdır.

```bash
git clone https://github.com/kullanici/stealth-engine.git
cd stealth-engine

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Gerekirse `.env` dosyasını düzenle, ardından başlat:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Dashboard: `http://localhost:8000`
- API dokümantasyonu: `http://localhost:8000/docs`

---

## API

| Method | Endpoint | Açiklama |
|---|---|---|
| GET | `/api/v1/health` | API ve proxy durumu |
| GET | `/api/v1/fingerprint/new` | Rastgele fingerprint üret |
| POST | `/api/v1/scrape` | Tek URL scrape et |
| POST | `/api/v1/scrape/multi` | Toplu URL scrape et |
| POST | `/api/v1/bot-check` | Bot tespit sayfasını ziyaret et |

```bash
curl -X POST http://localhost:8000/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "headless": true, "scroll": false}'
```

---

## Proxy Kullanimi

`data/proxies/proxies.txt` dosyasına her satıra bir proxy ekle:

```
http://kullanici:sifre@host:port
socks5://host:port
```

`.env` içinde etkinleştir:

```
PROXY_ENABLED=true
PROXY_ROTATION=true
```

---

## Dogrudan Kullanim

```python
from backend.core.browser import StealthBrowser
from backend.core.scraper import scraper

# Context manager ile
with StealthBrowser(headless=True) as browser:
    browser.go("https://example.com")
    browser.human_scroll(times=3)
    print(browser.title())

# Scraper servisi ile
result = scraper.scrape(
    url="https://example.com",
    scroll=True,
    headless=True,
    screenshot=True,
)
print(result["fingerprint"])
```

---

## Notlar

- `workers=1` kullan — undetected-chromedriver çoklu worker ile sorun çıkarabilir
- Bot tespit testi (`/api/v1/bot-check`) headful modda çalışır, Chrome penceresi açılır
- Proxy listesi boşsa bağlantı doğrudan yapılır

---

Bu proje yalnızca etik ve yasal amaçlar doğrultusunda kullanılmalıdır.
