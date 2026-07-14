"""FastAPI-приложение askbrows.

Два режима раздачи фронта:
- dev: фронт крутится отдельным Vite (STATIC_DIR пуст) — здесь только API.
- awwwdde-panel / прод: один контейнер, FastAPI отдаёт и /api, и собранную SPA
  из STATIC_DIR, а также /uploads. Порт 8080, healthcheck /healthz (контракт панели).
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.bot.webhook import router as bot_webhook_router
from app.core.config import settings
from app.modules.admin.appointments import router as admin_appointments_router
from app.modules.admin.auth import router as admin_auth_router
from app.modules.admin.clients import router as admin_clients_router
from app.modules.admin.schedule import router as admin_schedule_router
from app.modules.admin.services import router as admin_services_router
from app.modules.admin.settings import router as admin_settings_router
from app.modules.auth.router import router as auth_router
from app.modules.booking.router import router as booking_router
from app.modules.service.router import router as services_router

log = logging.getLogger("askbrows")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Настройка бота (menu button + webhook) и фоновый воркер напоминаний —
    # в single-container режиме панели всё живёт внутри веб-процесса.
    worker_task: asyncio.Task | None = None
    if settings.BOT_TOKEN:
        try:
            from app.bot.setup import setup_bot

            await setup_bot()
        except Exception:
            log.exception("Ошибка настройки бота (продолжаем без него)")
    if settings.RUN_REMINDER_WORKER:
        from app.workers.reminder_worker import run_loop

        worker_task = asyncio.create_task(run_loop())
        log.info("Reminder worker запущен фоновой задачей")
    try:
        yield
    finally:
        if worker_task is not None:
            worker_task.cancel()


app = FastAPI(
    title="askbrows API",
    version="0.1.0",
    description="Сайт-визитка + онлайн-запись + CRM + Telegram-бот для мастера-бровиста.",
    lifespan=lifespan,
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
app.include_router(bot_webhook_router, prefix="/api")

# CRM (админка) — все под /api/admin, защищены admin-cookie.
app.include_router(admin_auth_router, prefix="/api")
app.include_router(admin_services_router, prefix="/api")
app.include_router(admin_schedule_router, prefix="/api")
app.include_router(admin_settings_router, prefix="/api")
app.include_router(admin_clients_router, prefix="/api")
app.include_router(admin_appointments_router, prefix="/api")


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
