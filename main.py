"""
Stealth Engine — FastAPI entrypoint
Çalıştır: uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.api.routes import router
from backend.utils.logger import log
from config.settings import settings

app = FastAPI(
    title="Stealth Engine API",
    description="Anti-detection browser automation backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — frontend'in API'ye erişmesi için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API router
app.include_router(router)

# Frontend static dosyaları
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(str(frontend_path / "index.html"))


@app.on_event("startup")
async def startup():
    log.info("=" * 50)
    log.info("  STEALTH ENGINE API başlatıldı")
    log.info(f"  http://{settings.api_host}:{settings.api_port}")
    log.info(f"  Docs: http://{settings.api_host}:{settings.api_port}/docs")
    log.info("=" * 50)


@app.on_event("shutdown")
async def shutdown():
    log.info("Stealth Engine kapatıldı.")
