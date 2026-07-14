"""Воркер напоминаний: раз в минуту сканирует Reminder и отправляет готовые.

Модель из DECISIONS §2 — НЕ per-job APScheduler, а таблица + периодический скан:
    status='scheduled' AND send_at <= now()
Идемпотентность через sent_at. Фаза 1 — только скелет цикла; реальная отправка
через бота и ретраи — фаза 3.
"""

import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy import select

from app.database.session import async_session_maker
from app.models.enums import ReminderStatus
from app.models.reminder import Reminder

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("askbrows.worker")

SCAN_INTERVAL_SEC = 60


async def process_due_reminders() -> int:
    """Найти напоминания к отправке. Пока только логируем (фаза 3 подключит бота)."""
    now = datetime.now(UTC)
    async with async_session_maker() as session:
        result = await session.execute(
            select(Reminder).where(
                Reminder.status == ReminderStatus.scheduled,
                Reminder.send_at <= now,
            )
        )
        due = list(result.scalars().all())
        for reminder in due:
            # TODO(фаза 3): отправить через бота, при успехе — sent_at/status=sent,
            #               при ошибке — ретрай/failed. Пока только фиксируем находку.
            log.info("Напоминание #%s (%s) готово к отправке", reminder.id, reminder.type)
        return len(due)


async def main() -> None:
    log.info("Reminder worker запущен (скан раз в %s c).", SCAN_INTERVAL_SEC)
    while True:
        try:
            count = await process_due_reminders()
            if count:
                log.info("Обработано напоминаний: %s", count)
        except Exception:  # noqa: BLE001 — воркер не должен падать из-за одной итерации
            log.exception("Ошибка в цикле воркера")
        await asyncio.sleep(SCAN_INTERVAL_SEC)


if __name__ == "__main__":
    asyncio.run(main())
