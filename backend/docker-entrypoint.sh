#!/bin/sh
# Устойчивый старт askbrows в awwwdde-panel.
# Контейнер НЕ падает на сбое БД/миграции — поднимаем сервер, чтобы /healthz
# отвечал (панель видит живой контейнер), а причина видна в логах.

echo "[start] askbrows: запуск контейнера"

echo "[start] шаг 1/3: ожидание БД"
if ! python -m app.scripts.wait_for_db; then
    echo "[start] !!! БД недоступна. Сервер поднимется, но /api работать не будет."
    echo "[start] !!! Подключите Postgres к под-сайту и задайте DATABASE_URL, затем redeploy."
fi

echo "[start] шаг 2/3: миграции (alembic upgrade head)"
if ! alembic upgrade head; then
    echo "[start] !!! Миграции не применились. Возможные причины:"
    echo "[start] !!!  - нет доступа к БД (см. шаг 1);"
    echo "[start] !!!  - у пользователя БД нет прав на CREATE EXTENSION btree_gist."
fi

echo "[start] шаг 3/3: идемпотентный сид"
alembic_seed_ok=1
python -m app.scripts.seed || { echo "[start] !!! Сид не отработал (см. ошибку выше)"; alembic_seed_ok=0; }

echo "[start] запуск uvicorn на :8080 (seed_ok=${alembic_seed_ok})"
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
