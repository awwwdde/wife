"""Ожидание доступности БД перед миграциями (устойчивый старт в панели).

Пробуем подключиться к DATABASE_URL несколько раз — БД в панели может
подниматься чуть дольше приложения. Выход 0 — БД готова, 1 — не дождались.
"""

import asyncio
import sys

from sqlalchemy import text

from app.core.config import settings
from app.database.session import engine

ATTEMPTS = 30
DELAY_SEC = 2


async def main() -> int:
    # Скрываем пароль в логе.
    safe_url = settings.DATABASE_URL
    if "@" in safe_url:
        safe_url = safe_url.split("@", 1)[1]
    print(f"[wait_for_db] target: …@{safe_url}", flush=True)

    for i in range(1, ATTEMPTS + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print(f"[wait_for_db] database is ready (attempt {i})", flush=True)
            return 0
        except Exception as exc:  # noqa: BLE001 — логируем и повторяем
            print(f"[wait_for_db] attempt {i}/{ATTEMPTS} failed: {exc}", flush=True)
            await asyncio.sleep(DELAY_SEC)

    print(
        "[wait_for_db] БД недоступна после ретраев. Проверьте, что панель "
        "подключила Postgres и задан DATABASE_URL.",
        file=sys.stderr,
        flush=True,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
