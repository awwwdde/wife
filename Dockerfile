# ============================================================================
# askbrows — единый образ под awwwdde-panel (под-сайт).
#
# Контракт гостя панели:
#   • Dockerfile в корне репозитория (этот файл)
#   • приложение слушает порт 8080
#   • GET /healthz отдаёт 200, когда готово
#   • БД берётся из переменной окружения DATABASE_URL
#   • миграции/сид запускаются на старте контейнера
#
# Архитектура: фронт (Vite/React) собирается в статику и раздаётся тем же
# FastAPI-бэкендом, что обслуживает /api/* и /uploads/*. Один процесс, один порт.
# Бот и воркер напоминаний (Фаза 3) сюда не входят — это отдельные процессы.
# ============================================================================

# ── Stage 1: сборка фронта ──────────────────────────────────────────────────
FROM node:20-alpine AS frontend
WORKDIR /fe
RUN corepack enable

COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY frontend/ ./

# Build-time переменные Vite. Фронт и API — один origin, поэтому VITE_API_URL пуст
# (axios ходит на /api). Username бота не секрет — можно зашивать в бандл.
ARG VITE_BOT_USERNAME=askbrows_bot
ENV VITE_API_URL="" \
    VITE_BOT_USERNAME=${VITE_BOT_USERNAME}
RUN pnpm build

# ── Stage 2: рантайм ────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime
WORKDIR /app

# uv для установки зависимостей; curl — для healthcheck изнутри контейнера.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    ENV=production \
    STATIC_DIR=/app/static \
    UPLOADS_DIR=/app/uploads \
    RUN_REMINDER_WORKER=true

# Бэкенд-код + установка зависимостей (editable — import app из /app).
COPY backend/ ./
RUN uv pip install --system -e .

# Собранная SPA из stage 1 — её раздаёт сам FastAPI.
COPY --from=frontend /fe/dist /app/static

# Папка под загрузки админки (эфемерная без volume — переживает до redeploy).
RUN mkdir -p /app/uploads && chmod +x /app/docker-entrypoint.sh

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=5s --start-period=60s --retries=5 \
    CMD curl -fsS http://localhost:8080/healthz || exit 1

# Устойчивый старт: ждём БД → миграции → сид → uvicorn (:8080).
# Контейнер не падает на сбое БД/миграции — причина видна в логах, /healthz живёт.
CMD ["sh", "/app/docker-entrypoint.sh"]
