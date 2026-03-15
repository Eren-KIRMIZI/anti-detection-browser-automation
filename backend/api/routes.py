from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Optional

from backend.core.scraper import scraper
from backend.core.fingerprint import generate_fingerprint
from backend.utils.proxy_manager import proxy_manager
from backend.utils.logger import log

router = APIRouter(prefix="/api/v1", tags=["stealth"])


# ── Request / Response modelleri ──────────────────────────────────────────────

class ScrapeRequest(BaseModel):
    url: HttpUrl
    wait_css: Optional[str] = None
    scroll: bool = False
    headless: bool = True
    screenshot: bool = False


class MultiScrapeRequest(BaseModel):
    urls: list[HttpUrl]
    headless: bool = True
    scroll: bool = False


class BotCheckRequest(BaseModel):
    url: str = "https://bot.sannysoft.com"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/health")
def health():
    return {"status": "ok", "proxy_count": proxy_manager.count}


@router.get("/fingerprint/new")
def new_fingerprint():
    """Rastgele fingerprint üret (preview için)."""
    fp = generate_fingerprint()
    return {
        "user_agent": fp.user_agent,
        "languages": fp.languages,
        "timezone": fp.timezone,
        "resolution": f"{fp.width}x{fp.height}",
        "platform": fp.platform,
        "hardware_concurrency": fp.hardware_concurrency,
        "device_memory": fp.device_memory,
    }


@router.post("/scrape")
def scrape_url(req: ScrapeRequest):
    """Tek URL scrape et."""
    try:
        result = scraper.scrape(
            url=str(req.url),
            wait_css=req.wait_css,
            scroll=req.scroll,
            headless=req.headless,
            screenshot=req.screenshot,
        )
        # HTML büyük olabilir, isteğe göre kes
        result["html_length"] = len(result.get("html", ""))
        result["html"] = result["html"][:5000] + "..." if len(result.get("html","")) > 5000 else result["html"]
        return {"status": "ok", **result}
    except Exception as e:
        log.error(f"Scrape endpoint hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape/multi")
def scrape_multi(req: MultiScrapeRequest):
    """Birden fazla URL scrape et."""
    try:
        results = scraper.multi_scrape(
            urls=[str(u) for u in req.urls],
            headless=req.headless,
            scroll=req.scroll,
        )
        return {"status": "ok", "count": len(results), "results": results}
    except Exception as e:
        log.error(f"Multi-scrape hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bot-check")
def bot_check(req: BotCheckRequest):
    """Bot tespit sayfasını ziyaret et ve screenshot al."""
    try:
        result = scraper.check_bot_detection(req.url)
        return {"status": "ok", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proxy/status")
def proxy_status():
    return {
        "total": proxy_manager.count,
        "rotation": True,
    }
