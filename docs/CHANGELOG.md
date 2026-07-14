# CHANGELOG
История проекта. Формат записей: `ASKBROWS: X.Y — заголовок`.

## ASKBROWS: 3.0 — Фаза 3: Telegram-бот и уведомления (2026-07-14)
- Бот на **webhook внутри FastAPI** (`/api/bot/webhook`) — на панели отдельный процесс не нужен.
- `/start` с кнопками **Mini App** (замена DIKIDI) и **«Поделиться номером»**; приём контакта → `Client.phone`.
- На старте: `setWebhook` + menu-кнопка `web_app` (по https из `PUBLIC_SITE_URL`).
- **Воркер напоминаний** реально шлёт: подтверждение / за 24ч / за 2ч / запрос отзыва (адрес отдаётся после записи), идемпотентно; на панели — фоновой задачей (`RUN_REMINDER_WORKER`).
- Инлайн-кнопки «Подтверждаю»/«Отменить» (с правилом 6ч) в уведомлениях.

## ASKBROWS: 2.2 — Фикс prod-сборки фронта (2026-07-14)
- axios baseURL: `||` вместо `??` — пустой `VITE_API_URL` в prod теперь даёт `/api` (запросы не теряли префикс).
- Защита от не-массивных ответов API (нет падения `t.map`). Устойчивый старт контейнера (`docker-entrypoint.sh`, `wait_for_db`).

## ASKBROWS: 2.1 — Готовность к awwwdde-panel (2026-07-14)
- Корневой `Dockerfile`: единый образ (фронт-статика + FastAPI), порт 8080, `/healthz`,
  миграции+сид на старте. `.dockerignore`.
- FastAPI отдаёт собранную SPA из `STATIC_DIR` (+ фолбэк на `index.html`), монтирует
  `/uploads`; неизвестные `/api/*` → 404 JSON.
- `DATABASE_URL` авто-нормализуется к asyncpg (`postgres://`/`postgresql://`/`+psycopg2`).
- Документация: `docs/DEPLOY-PANEL.md`, `docs/API.md`, секция деплоя в README.

## ASKBROWS: 2.0 — Фаза 2: запись + Telegram-авторизация (2026-07-14)
- Валидация подписи Telegram: `initData` (Mini App) и Login Widget (браузер) + `auth_date`.
- JWT в httpOnly-cookie; модуль `auth` (`/auth/telegram/miniapp|widget`, `/auth/me`, `/auth/logout`).
- Расчёт свободных слотов (график − отпуска − занятые, буфер/шаг/таймзона).
- Создание записи с защитой от двойного бронирования (EXCLUDE → 409), мультиуслуга,
  `my`/`cancel`/`reschedule` (правило 6ч), заготовки строк `Reminder`.
- Фронт (без стилей): `AuthProvider`, поток записи, личный кабинет, страница политики ПДн.
- Токен бота @askbrows_bot получен и хранится в локальном `.env`.

## ASKBROWS: 1.2 — Единая dev-команда (2026-07-14)
- `pnpm run dev` поднимает Postgres (docker), бэк и фронт с цветными логами
  (голубой DB / зелёный BACK / фиолетовый FRONT). `db:init` — миграции+сид.

## ASKBROWS: 1.1 — Фаза 1: скелет монорепо (2026-07-14)
- `/frontend` (Vite+React+TS+Tailwind, pnpm), `/backend` (FastAPI+SQLAlchemy 2.0
  async+Alembic, uv+ruff), docker-compose (postgres, redis, bot, worker).
- Полная схема БД + миграция `0001_init` (btree_gist + EXCLUDE-констрейнт), демо-сид.
- Витрина услуг из API, базовая интеграция Lenis/GSAP/Framer.

## ASKBROWS: 1.0 — Сбор требований (2026-06-26)
- `SPEC.md`, `DECISIONS.md`, `SESSIONS.md`, `PROJECT_BIBLE.md`. Кода нет.
