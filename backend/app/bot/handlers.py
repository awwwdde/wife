"""Обработчики бота: /start, приём контакта (телефон), подтверждение/отмена."""

import logging
from datetime import UTC, datetime, timedelta

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import start_keyboard
from app.core.config import settings
from app.core.telegram_auth import TelegramUser
from app.database.session import async_session_maker
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.modules.client import repository as client_repo

log = logging.getLogger("askbrows.bot")
router = Router()

WELCOME = (
    "Привет! Это бот записи askbrows 💫\n\n"
    "Нажмите «Записаться», чтобы выбрать услугу и время, "
    "и «Поделиться номером», чтобы мы могли связаться с вами."
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME, reply_markup=start_keyboard(settings.PUBLIC_SITE_URL))


@router.message(F.contact)
async def on_contact(message: Message) -> None:
    """Клиент поделился номером — сохраняем и связываем с Client."""
    contact = message.contact
    user = message.from_user
    if contact is None or user is None:
        return
    async with async_session_maker() as session:
        client = await client_repo.get_or_create_by_telegram(
            session,
            TelegramUser(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
            ),
        )
        await client_repo.set_phone(session, client, contact.phone_number)
        await session.commit()
    await message.answer("Спасибо! Номер сохранён. Теперь можно записываться.")


@router.callback_query(F.data.startswith("ap:"))
async def on_appointment_action(callback: CallbackQuery) -> None:
    """Инлайн-подтверждение/отмена записи из уведомления."""
    if callback.data is None or callback.from_user is None:
        return
    try:
        _, action, raw_id = callback.data.split(":")
        appointment_id = int(raw_id)
    except ValueError:
        await callback.answer("Некорректная кнопка")
        return

    async with async_session_maker() as session:
        client = await client_repo.get_by_telegram_id(session, callback.from_user.id)
        appt = await session.get(Appointment, appointment_id)
        if appt is None or client is None or appt.client_id != client.id:
            await callback.answer("Запись не найдена")
            return

        if action == "cf":  # подтвердить
            if appt.status == AppointmentStatus.pending:
                appt.status = AppointmentStatus.confirmed
                await session.commit()
            await callback.answer("Запись подтверждена ✅")
            await callback.message.answer("Спасибо, ждём вас!")
        elif action == "cx":  # отменить (правило N часов)
            deadline = appt.start_at - timedelta(hours=settings.CANCELLATION_HOURS)
            if appt.status not in (AppointmentStatus.pending, AppointmentStatus.confirmed):
                await callback.answer("Эту запись уже нельзя изменить")
            elif datetime.now(UTC) > deadline:
                await callback.answer(
                    f"Отмена возможна не позднее {settings.CANCELLATION_HOURS} ч до визита"
                )
            else:
                appt.status = AppointmentStatus.cancelled
                await session.commit()
                await callback.answer("Запись отменена")
                await callback.message.answer("Запись отменена. Будем рады видеть вас снова!")
        else:
            await callback.answer()
