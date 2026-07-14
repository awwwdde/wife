"""FastAPI-приложение askbrows.

Два режима раздачи фронта:
- dev: фронт крутится отдельным Vite (STATIC_DIR пуст) — здесь только API.
- awwwdde-panel / прод: один контейнер, FastAPI отдаёт и /api, и собранную SPA
  из STATIC_DIR, а также /uploads. Порт 8080, healthcheck /healthz (контракт панели).
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.booking.router import router as booking_router
from app.modules.service.router import router as services_router

app = FastAPI(
    title="askbrows API",
    version="0.1.0",
    description="Сайт-визитка + онлайн-запись + CRM + Telegram-бот для мастера-бровиста.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz", tags=["system"])
async def healthz() -> dict[str, str]:
    """Healthcheck для панели: 200 когда приложение готово."""
    return {"status": "ok"}


@app.get("/api/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.ENV}


# Роутеры под /api.
app.include_router(services_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(booking_router, prefix="/api")


# --- Раздача загрузок (медиа) ---
if settings.UPLOADS_DIR and Path(settings.UPLOADS_DIR).is_dir():
    app.mount("/uploads", StaticFiles(directory=settings.UPLOADS_DIR), name="uploads")


# --- Раздача собранной SPA (single-container режим) ---
if settings.STATIC_DIR and Path(settings.STATIC_DIR).is_dir():
    _static = Path(settings.STATIC_DIR)

    # Ассеты Vite (хэшированные, кэшируемые).
    _assets = _static / "assets"
    if _assets.is_dir():
        app.mount("/assets", StaticFiles(directory=str(_assets)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str) -> FileResponse:
        """Отдаём файл из статики, иначе index.html (клиентский роутинг SPA).

        Пути под API/загрузками/healthz — это бэкенд: несуществующие отдаём 404,
        а не HTML SPA.
        """
        if full_path.startswith(("api/", "uploads/", "assets/")) or full_path == "healthz":
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        candidate = _static / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_static / "index.html")
