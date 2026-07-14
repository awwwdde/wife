"""Воркер напоминаний: раз в минуту сканирует Reminder и рассылает через бота.

Модель из DECISIONS §2 — НЕ per-job APScheduler, а таблица + периодический скан:
    status='scheduled' AND send_at <= now()
Идемпотентность через sent_at/status. На панели воркер запускается фоновой
задачей внутри веб-процесса (RUN_REMINDER_WORKER=true); в docker-compose — отдельный сервис.
"""

import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy import select

from app.core.config import settings
from app.database.session import async_session_maker
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus, ReminderStatus
from app.models.reminder import Reminder

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("askbrows.worker")

SCAN_INTERVAL_SEC = 60

# Записи, для которых уведомления слать не нужно.
_SKIP_STATUSES = (AppointmentStatus.cancelled, AppointmentStatus.no_show)


async def process_due_reminders() -> int:
    """Отправить готовые напоминания. Возвращает число отправленных."""
    if not settings.BOT_TOKEN:
        return 0  # без токена слать нечем (скелет/локалка)

    from aiogram.exceptions import TelegramNetworkError

    from app.bot import notifications

    now = datetime.now(UTC)
    sent = 0
    async with async_session_maker() as session:
        result = await session.execute(
            select(Reminder).where(
                Reminder.status == ReminderStatus.scheduled,
                Reminder.send_at <= now,
            )
        )
        due = list(result.scalars().all())
        for reminder in due:
            appt = await session.get(Appointment, reminder.appointment_id)
            try:
                if appt is None or appt.status in _SKIP_STATUSES:
                    reminder.status = ReminderStatus.failed  # неактуально
                    continue
                ok = await notifications.send_reminder(session, appt, reminder.type)
                if ok:
                    reminder.status = ReminderStatus.sent
                    reminder.sent_at = datetime.now(UTC)
                    sent += 1
                else:
                    reminder.status = ReminderStatus.failed
            except TelegramNetworkError:
                # Сеть до Telegram недоступна — НЕ теряем напоминание, повторим позже.
                log.warning("Сеть до Telegram недоступна — #%s на повтор", reminder.id)
            except Exception:
                log.exception("Не удалось отправить напоминание #%s", reminder.id)
                reminder.status = ReminderStatus.failed
        await session.commit()
    return sent


async def run_loop() -> None:
    log.info("Reminder worker запущен (скан раз в %s c).", SCAN_INTERVAL_SEC)
    while True:
        try:
            count = await process_due_reminders()
            if count:
                log.info("Отправлено напоминаний: %s", count)
        except Exception:
            log.exception("Ошибка в цикле воркера")
        await asyncio.sleep(SCAN_INTERVAL_SEC)


if __name__ == "__main__":
    asyncio.run(run_loop())
