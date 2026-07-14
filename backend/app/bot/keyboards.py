"""Клавиатуры бота."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)


def start_keyboard(webapp_url: str | None) -> ReplyKeyboardMarkup:
    """Reply-клавиатура: поделиться номером + (если есть https) открыть Mini App."""
    rows: list[list[KeyboardButton]] = [
        [KeyboardButton(text="📱 Поделиться номером", request_contact=True)],
    ]
    if webapp_url and webapp_url.startswith("https://"):
        rows.append(
            [KeyboardButton(text="✍️ Записаться", web_app=WebAppInfo(url=webapp_url))]
        )
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def appointment_actions(appointment_id: int, with_confirm: bool = True) -> InlineKeyboardMarkup:
    """Инлайн-кнопки под уведомлением: подтвердить / отменить."""
    rows: list[list[InlineKeyboardButton]] = []
    if with_confirm:
        rows.append(
            [InlineKeyboardButton(text="✅ Подтверждаю", callback_data=f"ap:cf:{appointment_id}")]
        )
    rows.append(
        [InlineKeyboardButton(text="❌ Отменить", callback_data=f"ap:cx:{appointment_id}")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
