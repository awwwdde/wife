# askbrows — Журнал сессий

> Хронология работы для продолжения с любого устройства. **Самая свежая сессия — сверху.**
> В конце каждой сессии добавляется блок: **Что обсудили · Что сделали · Что осталось**.
> Стабильные решения живут в [`DECISIONS.md`](DECISIONS.md), требования — в [`../SPEC.md`](../SPEC.md).

---

## Сессия 5 — 2026-07-14

### Что обсудили
- Деплой на панель заработал (панель дала Postgres `askbrows_db`). По логам поймали баг: prod-сборка звала `/services` без `/api` (`??` не заменял пустую строку) → пофикшено `||` + защита от не-массивов. Договорились дальше делать **Фазу 3 (бот)**.

### Что сделали (Фаза 3 — бот и уведомления)
- **Бот через webhook внутри FastAPI** (`app/bot/webhook.py` → `/api/bot/webhook`, проверка secret). На панели отдельный процесс не нужен.
- Хендлеры (`app/bot/handlers.py`): `/start` (кнопки Mini App + «Поделиться номером»), приём `contact` → сохранение телефона в `Client`, инлайн `Подтверждаю/Отменить` (правило 6ч).
- `app/bot/setup.py`: на старте `setWebhook` + menu-кнопка `web_app` (замена DIKIDI), только по https из `PUBLIC_SITE_URL`.
- `app/bot/notifications.py`: тексты подтверждения / за 24ч / за 2ч / отзыва (адрес — только после записи).
- Воркер (`reminder_worker.py`) реально шлёт due-напоминания, идемпотентно; на панели — фоновая задача в `main.py` lifespan (`RUN_REMINDER_WORKER=true` в образе). Локально compose — отдельный процесс/polling (`app/bot/__main__.py`).
- **Проверено:** ruff чисто, все bot-модули импортируются, `/api/bot/webhook` смонтирован (13 роутов). getMe бота — ок (@askbrows_bot).

### Что осталось (следующий шаг)
- [ ] Задать на панели `PUBLIC_SITE_URL=https://<поддомен>` и `TELEGRAM_WEBHOOK_SECRET`, redeploy. Проверить `/start`, шаринг номера, запись → приходит подтверждение; отмена инлайн-кнопкой.
- [ ] Живой e2e бота (написать боту, пройти запись) — требует задеплоенного webhook.
- [ ] **Фаза 4 — CRM** (`/admin110220`): вход 2FA, календарь, клиенты, услуги/график CRUD, ручные записи. Сейчас данные только из демо-сида.

---

## Сессия 4 — 2026-07-14

### Что обсудили
- Заказчик выкладывает askbrows в **awwwdde-panel** как под-сайт. Docker Desktop у него нет — образ собирает панель на сервере из репозитория.
- Разобрали контракт гостя панели по образцу проекта «Дом Союзов» (Dockerfile в корне, порт 8080, `/healthz`, `DATABASE_URL`, миграции/сид на старте).

### Что сделали (готовность к панели)
- **Корневой `Dockerfile`** — единый образ: фронт (Vite) → статика, раздаётся тем же FastAPI, что и `/api`; порт 8080; `HEALTHCHECK` на `/healthz`; на старте `alembic upgrade head` + сид. Плюс `.dockerignore`.
- **`main.py`**: `GET /healthz`; раздача SPA из `STATIC_DIR` (фолбэк `index.html`, клиентский роутинг), `/uploads`; неизвестные `/api/*` → 404 JSON.
- **`config.py`**: нормализация `DATABASE_URL` к asyncpg; `STATIC_DIR`/`UPLOADS_DIR`.
- **Документация:** `docs/DEPLOY-PANEL.md` (гайд деплоя + env), `docs/API.md` (справочник эндпоинтов), обновлён `docs/CHANGELOG.md` (формат ASKBROWS), секция деплоя в README.
- **Проверено вживую** (тот же рантайм, что в контейнере): `/healthz` 200; `/` и `/booking` → SPA; `/api/health` JSON; `/api/nope` → 404 JSON; ассеты 200; `DATABASE_URL` 4 формата → asyncpg; ruff чисто; `pnpm build` зелёный. `docker build` не гоняли — Docker Desktop недоступен (соберёт панель).

### Что осталось (следующий шаг)
- [ ] **Закоммитить + запушить** в `origin` (github.com/awwwdde/wife) — панель собирает из репозитория.
- [ ] В панели: создать под-сайт на этот репозиторий, задать env (`DATABASE_URL`, `JWT_SECRET`, `BOT_TOKEN`), собрать. Проверить `/healthz`, `/api/services`, запись.
- [ ] BotFather `/setdomain <поддомен>` — для браузерного Login Widget.
- [ ] **Фаза 3** — бот: кнопка Mini App вместо DIKIDI, `/start` + `request_contact`, webhook в тот же FastAPI, реальная отправка `Reminder` воркером.

---

## Сессия 3 — 2026-07-14

### Что обсудили
- Заказчик прислал **токен бота** (сохранён только в локальном `.env`, в репозиторий не коммитится). Бот: **@askbrows_bot** (проверено через getMe).
- Согласовали пофайловый план Фазы 2 и договорились: **без стилей** — стандартные HTML-элементы, дизайн определим позже.

### Что сделали (Фаза 2 — запись + Telegram-auth)
- **Backend:**
  - `core/telegram_auth.py` — валидация подписи `initData` (HMAC-SHA256 + "WebAppData") и Login Widget (`hash`), проверка `auth_date`. Покрыто ручным тестом (валид/подделка).
  - `core/security.py` — JWT + httpOnly-cookie (`set/clear`).
  - Модуль `auth`: `POST /api/auth/telegram/miniapp`, `/widget`, `GET /api/auth/me`, `POST /api/auth/logout`; зависимость `get_current_client`.
  - Модуль `booking`: `slots.py` (WorkingHours − TimeOff − занятые, с буфером/шагом/tz; юнит-тест ок), `POST /api/appointments` с защитой от двойного бронирования (EXCLUDE → 409), `GET /api/appointments/my`, `cancel`/`reschedule` (правило 6ч), заготовка строк `Reminder`.
  - `config.py` теперь читает **корневой `.env`** абсолютным путём (локальный запуск с cwd=backend). Добавлена зависимость **tzdata** (Windows не имеет IANA-базы для zoneinfo).
- **Frontend (без стилей):** `AuthProvider` (авто-вход в Mini App по `initData`, восстановление сессии по cookie в браузере), `TelegramLoginWidget`, поток записи `BookingWizard` (услуги → дата/слот → авторизация → согласие ПДн → подтверждение, обработка 409), `CabinetPage` (мои записи + отмена), `PrivacyPage` (шаблон 152-ФЗ с плейсхолдерами реквизитов). Роут `/privacy`, `VITE_BOT_USERNAME`.
- **Проверено:** ruff — чисто; 11 API-роутов монтируются; валидатор `initData` (валид+подделка); алгоритм слотов (3 кейса); `pnpm build` — зелёный.

### Что осталось (следующий шаг)
- [ ] **Живой e2e с Postgres** (сейчас Docker Desktop был выключен): `pnpm run dev` → `pnpm run db:init` → пройти запись в Mini App/через API: создание клиента по `initData`, слоты, `POST /appointments`, конфликт 409, отмена по правилу 6ч.
- [ ] Привязать домен бота в BotFather (`/setdomain askbrows.awwwdde.art`) — иначе браузерный Login Widget не отображается.
- [ ] Закоммитить Фазы 1–2 (+ `uv.lock`, `pnpm-lock.yaml`).
- [ ] **Фаза 3** — бот: замена кнопки DIKIDI на Mini App, `/start` + `request_contact` (сбор телефона), webhook, реальная отправка `Reminder` воркером, инлайн-подтверждение/отмена.

---

## Сессия 2 — 2026-07-14

### Что обсудили
- Уточнили вводные перед стартом кода: цель сессии — **скаффолдинг Фазы 1**; бот-токен придёт позже (проектируем на плейсхолдерах `.env`); ПДн-оператор — **оформляется самозанятость/ИП** (реквизиты в политику впишем позже); экспорт DIKIDI — уточняется.
- Согласовали тех-решения Фазы 1 (см. `DECISIONS.md` §7): лейаут репо `/frontend` + `/backend` (бот и воркер — отдельные процессы из образа backend), прагматичный минимум архитектуры, pnpm, uv+ruff, self-host шрифты, dev — Vite HMR / prod — Nginx.

### Что сделали
- **Корень:** `docker-compose.yml` (frontend/backend/bot/worker/postgres/redis), `.env.example`, `.gitignore`.
- **Backend:** FastAPI-скелет (`GET /api/health`, `GET /api/services`), `core/config` (pydantic-settings), async-БД (engine/session/Base), **все модели** (Master, Client, Service, Appointment + M2M `appointment_services`, WorkingHours, TimeOff, Reminder, Review) с правками DECISIONS §5, миграция `0001_init` с `btree_gist` + EXCLUDE-констрейнтом, каркасы бота (aiogram) и воркера напоминаний, демо-сид, `pyproject`/`ruff`/`Dockerfile`.
- **Frontend:** Vite+React18+TS+Tailwind, палитра/шрифты из DECISIONS §4, Lenis+GSAP+Framer (SmoothScroll), определение режима браузер/Mini App, витрина услуг из API, роутер с ленивым `/admin110220`, заглушки Booking/Cabinet/Admin, Dockerfile.dev/Dockerfile + nginx.
- **Проверено:** frontend `pnpm build` — зелёный; backend — все 9 таблиц регистрируются, модели/EXCLUDE импортируются без ошибок.

### Что осталось (следующий шаг)
- [ ] Поднять стек `docker compose up` на реальной машине, применить `alembic upgrade head` + `python -m app.scripts.seed`, проверить витрину услуг из БД end-to-end.
- [ ] Зафиксировать `uv.lock` (backend) и `pnpm-lock.yaml` в репозиторий.
- [ ] Начать **Фазу 2**: определение режима + авторизация (Login Widget / `initData` с валидацией подписи), расчёт свободных слотов, создание записи с защитой от двойного бронирования.
- [ ] От заказчика: токен/username бота; статус оператора ПДн (реквизиты); (позже) экспорт DIKIDI и домен `askbrows.ru`.

---

## Сессия 1 — 2026-06-26

### Что обсудили
- Прочитали и разобрали `SPEC.md` (сайт-визитка + онлайн-запись + CRM + Telegram-бот, уход с DIKIDI).
- Зафиксировали все ключевые архитектурные решения и контент-вводные (детали — в `DECISIONS.md`):
  - админка `/admin110220` с 2FA; напоминания через таблицу + воркер раз/мин; хостинг Timeweb (РФ); SEO не приоритет;
  - отмена за 6ч; ручные исходы записи (`completed`/`cancelled`/`no_show`); ЛК клиента сразу; мультиуслуга; буфер на уровне услуги; отзывы через бота; без онлайн-оплаты; только русский;
  - бренд: Ангелина / askbrows, Москва, домашняя студия (адрес приватный); услуги/график/портфолио мастер вносит сам; логотип текстовый ASKBROWS; временный домен `askbrows.awwwdde.art`.
- Согласовали правки к модели данных ТЗ: `Appointment↔Service` many-to-many, `Service.buffer_min`, модель `Review`, приватный адрес/`slot_step_min`/`cancellation_hours` в настройках мастера, `Client.consent_at`.
- Отметили риски: ПДн без оформленного оператора; ждём токен/username бота; миграция из DIKIDI под вопросом.

### Что сделали
- Скопировали `SPEC.md` в корень репозитория.
- Завели `docs/DECISIONS.md` (источник истины по решениям) и `docs/SESSIONS.md` (этот журнал).
- Кода ещё **не писали** — были на стадии сбора требований.

### Что осталось (следующий шаг)
- [ ] Показать заказчику **пофайловый план Фазы 1** (монорепо-скелет `/frontend`, `/backend`, `/bot`, docker-compose, схема БД с правками из `DECISIONS.md` §5) — и получить «погнали».
- [ ] После утверждения — скаффолдинг Фазы 1.
- [ ] Получить от заказчика: токен/username бота; статус оператора ПДн; (позже) реквизиты домена `askbrows.ru`.

---

<!--
ШАБЛОН НОВОЙ СЕССИИ (копировать наверх):

## Сессия N — YYYY-MM-DD

### Что обсудили
-

### Что сделали
-

### Что осталось (следующий шаг)
- [ ]
-->
