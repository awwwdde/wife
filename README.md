# askbrows

Сайт-визитка + онлайн-запись + CRM + Telegram-бот для мастера-бровиста (Ангелина, бренд *askbrows*, Москва). Уход с DIKIDI на собственную систему.

## Где что лежит
- [`docs/SPEC.md`](SPEC.md) — техническое задание (источник истины по требованиям).
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — принятые решения и правки к ТЗ (читать первым при продолжении работы).
- [`docs/SESSIONS.md`](docs/SESSIONS.md) — журнал сессий: что обсудили / сделали / осталось.
- [`docs/PROJECT_BIBLE.md`](docs/PROJECT_BIBLE.md) — Библия проекта.
- [`docs/CHANGELOG.md`](docs/CHANGELOG.md) — Записи обновлений формата (ASKBROWS: 1.1 Старт разработки).

## Как продолжать сессию (с любого устройства)
1. Прочитать `docs/SESSIONS.md` — верхний блок = текущее состояние и следующий шаг.
2. Свериться с `docs/DECISIONS.md` по решениям.
3. В конце работы — **дописать новый блок сессии наверх** `docs/SESSIONS.md` (шаблон внизу файла).
4. По команде "обновление" - **записать обновление формата ASKBROWS: 1.1 Старт разработки** `docs/CHANGELOG.md`
5. Дополнять Библию проекта новыми идеями `docs/PROJECT_BIBLE.md`

## Стек
Frontend: Vite + React 18 + TS + Tailwind + Framer Motion + GSAP + Lenis · TanStack Query · RHF + Zod.
Backend: FastAPI + SQLAlchemy 2.0 async + Alembic + Pydantic v2 · PostgreSQL · Redis.
Bot: aiogram 3.x (webhook на проде). Деплой: docker-compose, хостинг Timeweb (РФ).

## Статус
Фазы 1–2 готовы (сайт-визитка, онлайн-запись, Telegram-авторизация, защита от двойного бронирования) и проект собран в **единый образ под awwwdde-panel**. Следующий шаг: выложить на под-сайт (см. [`docs/DEPLOY-PANEL.md`](docs/DEPLOY-PANEL.md)) и Фаза 3 (бот + уведомления). Подробности — в [`docs/SESSIONS.md`](docs/SESSIONS.md).

Документы: [`SPEC.md`](SPEC.md) · [`docs/DECISIONS.md`](docs/DECISIONS.md) · [`docs/SESSIONS.md`](docs/SESSIONS.md) · [`docs/API.md`](docs/API.md) · [`docs/DEPLOY-PANEL.md`](docs/DEPLOY-PANEL.md) · [`docs/CHANGELOG.md`](docs/CHANGELOG.md) · [`docs/PROJECT_BIBLE.md`](docs/PROJECT_BIBLE.md)

## Быстрый старт (dev) — одна команда
Поднимает БД, бэк и фронт вместе, с цветными логами:
**голубой `[DB]`** (Postgres :5432, docker) · **зелёный `[BACK]`** (FastAPI :8000) · **фиолетовый `[FRONT]`** (Vite :5173).
```bash
pnpm install        # один раз: ставит concurrently в корне
pnpm run dev        # поднимает Postgres + бэк + фронт
pnpm run db:init    # один раз при первом старте: миграции + демо-сид
```
Требования: Node ≥ 20 + pnpm, Python ≥ 3.12, `uv` (`python -m pip install uv`; скрипты зовут его через `python -m uv`), **Docker Desktop запущен** (для `[DB]`).
- Первый запуск бэка сам создаёт `backend/.venv` и ставит зависимости.
- Если Docker не запущен — `[DB]` упадёт, но бэк и фронт продолжат работать (`/api/health` ок; `/api/services` заработает после `db:init`).
- Локально бэк ходит в БД на `localhost:5432`; в docker-compose — на хост `postgres` (переопределяется автоматически).

Отдельные части: `pnpm run dev:db` · `pnpm run dev:back` · `pnpm run dev:front`.

## Полный стек (docker-compose)
```bash
cp .env.example .env                 # заполнить секреты
docker compose up --build            # frontend :5173, backend :8000, postgres, redis, bot, worker
# в отдельном терминале, после старта postgres:
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.scripts.seed
```

## Деплой как под-сайт (awwwdde-panel)
Корневой **`Dockerfile`** собирает единый образ по контракту панели: фронт (Vite) → статика, раздаётся тем же FastAPI, что и `/api`. Один процесс, один порт.

Контракт гостя (выполнен):
- Dockerfile в корне · слушает порт **8080** · `GET /healthz` → 200 · БД из **`DATABASE_URL`** · миграции+сид на старте.

Панель должна передать переменные окружения:
| Переменная | Обязательна | Назначение |
|---|---|---|
| `DATABASE_URL` | **да** | Postgres (любой из `postgres://`/`postgresql://`/`+psycopg2` — приводится к asyncpg). SQLite не поддерживается (нужны EXCLUDE/btree_gist/ARRAY/enum). |
| `JWT_SECRET` | **да** | подпись cookie-сессий (иначе небезопасный дефолт). |
| `BOT_TOKEN` | да (для входа) | валидация Telegram `initData`/Login Widget. |
| `CORS_ORIGINS` | нет | не нужен при том же origin (фронт и API из одного контейнера). |

`ENV=production`, `STATIC_DIR`, `UPLOADS_DIR` уже заданы в образе. Username бота вшивается на сборке (`--build-arg VITE_BOT_USERNAME=...`, дефолт `askbrows_bot`).

Локальная проверка образа:
```bash
docker build -t askbrows .
docker run -p 8080:8080 -e DATABASE_URL=postgresql+asyncpg://user:pass@host/db -e JWT_SECRET=xxx askbrows
# → http://localhost:8080  (SPA), /healthz, /api/*
```
> Бот и воркер напоминаний (Фаза 3) в этот образ не входят — это отдельные процессы. Для браузерного Login Widget нужно привязать домен бота в BotFather (`/setdomain`).
