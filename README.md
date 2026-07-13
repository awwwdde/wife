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
Фаза 0 — сбор требований завершён. Следующий шаг: план Фазы 1 (монорепо-скелет). Подробности — в `docs/SESSIONS.md`.
