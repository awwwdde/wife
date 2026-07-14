"""Единая конфигурация из переменных окружения (pydantic-settings).

Секреты только из .env — ничего не хардкодим (см. SPEC §11, DECISIONS §6).
"""

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корневой .env (на уровень выше backend/): backend/app/core/config.py → parents[3].
# Читаем его абсолютным путём, чтобы локальный запуск с cwd=backend видел секреты.
# В docker переменные приходят из окружения и имеют приоритет над файлом.
_ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(_ROOT_ENV), ".env"), extra="ignore"
    )

    ENV: str = "development"
    TZ: str = "Europe/Moscow"

    # Домены
    PUBLIC_SITE_URL: str = "http://localhost:5173"
    PUBLIC_API_URL: str = "http://localhost:8000"

    # БД / Redis.
    # Дефолт — localhost (локальный `pnpm run dev`: бэк на хосте, postgres в docker
    # опубликован на localhost:5432). В docker-compose host переопределяется на `postgres`.
    DATABASE_URL: str = "postgresql+asyncpg://askbrows:change-me@localhost:5432/askbrows"
    REDIS_URL: str = "redis://redis:6379/0"

    # Auth / JWT
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_TTL_MIN: int = 43200

    # Telegram (заполним на фазе 2–3)
    BOT_TOKEN: str = ""
    BOT_USERNAME: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = "change-me"
    # Прокси для api.telegram.org, если у хостинга нет прямого исходящего доступа
    # к Telegram (напр. "http://user:pass@host:port" или "socks5://host:port").
    TELEGRAM_PROXY: str = ""
    # Свой base-URL Bot API (реверс-прокси, напр. Cloudflare Worker) — когда прямой
    # доступ к api.telegram.org закрыт. Напр. "https://xxx.workers.dev".
    TELEGRAM_API_BASE: str = ""

    # Бизнес-правила
    CANCELLATION_HOURS: int = 6

    # Запускать воркер напоминаний внутри веб-процесса (single-container режим панели).
    # В docker-compose воркер — отдельный сервис, поэтому здесь по умолчанию False.
    RUN_REMINDER_WORKER: bool = False

    # S3
    S3_ENDPOINT: str = ""
    S3_BUCKET: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_REGION: str = "ru-1"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # Раздача SPA одним процессом (режим awwwdde-panel: FastAPI отдаёт статику).
    # Пусто → статика не монтируется (dev: фронт крутит отдельный Vite).
    STATIC_DIR: str = ""
    UPLOADS_DIR: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _normalize_db_url(cls, v: str) -> str:
        """Приводим DATABASE_URL к async-драйверу asyncpg.

        Панель/хостинг может выдать `postgres://`, `postgresql://` или
        `postgresql+psycopg2://` — все переводим в `postgresql+asyncpg://`.
        """
        if not isinstance(v, str):
            return v
        for prefix in ("postgresql+psycopg2://", "postgresql://", "postgres://"):
            if v.startswith(prefix):
                return "postgresql+asyncpg://" + v[len(prefix):]
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
