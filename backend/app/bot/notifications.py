"""Сборка и отправка уведомлений клиенту через бота."""

import logging
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import get_bot
from app.bot.keyboards import appointment_actions
from app.models.appointment import Appointment
from app.models.enums import ReminderType
from app.modules.client.models import Client
from app.modules.settings.repository import get_default_master

log = logging.getLogger("askbrows.bot")


def _fmt_when(appt: Appointment, tz_name: str) -> str:
    local = appt.start_at.astimezone(ZoneInfo(tz_name))
    return local.strftime("%d.%m в %H:%M")


async def send_reminder(session: AsyncSession, appt: Appointment, rtype: ReminderType) -> bool:
    """Отправить клиенту сообщение по записи. True — отправлено."""
    client = await session.get(Client, appt.client_id)
    if client is None or client.telegram_id is None:
        log.warning("Напоминание #%s: у клиента нет telegram_id — пропуск", appt.id)
        return False

    master = await get_default_master(session)
    tz_name = master.timezone if master else "Europe/Moscow"
    when = _fmt_when(appt, tz_name)
    services = ", ".join(s.title for s in appt.services)
    address = (master.address if master and master.address else "уточним отдельно")

    bot = get_bot()
    markup = None

    if rtype is ReminderType.confirmation:
        text = (
            f"Ваша запись принята ✨\n{services}\n{when}\n\n"
            f"Адрес: {address}\n\nПодтвердите, пожалуйста:"
        )
        markup = appointment_actions(appt.id, with_confirm=True)
    elif rtype is ReminderType.day_before:
        text = f"Напоминаем: завтра {when} — {services}.\nАдрес: {address}"
        markup = appointment_actions(appt.id, with_confirm=False)
    elif rtype is ReminderType.hours_before:
        text = f"Совсем скоро: сегодня {when} — {services}.\nАдрес: {address}\nЖдём вас!"
    elif rtype is ReminderType.review_request:
        text = "Спасибо за визит! Будем благодарны за отзыв 🌿"
    else:
        return False

    await bot.send_message(chat_id=client.telegram_id, text=text, reply_markup=markup)
    return True
