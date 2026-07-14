"""Настройка бота на старте: menu button (Mini App вместо DIKIDI) + webhook."""

import logging

from aiogram.types import MenuButtonWebApp, WebAppInfo

from app.bot import get_bot
from app.core.config import settings

log = logging.getLogger("askbrows.bot")

WEBHOOK_PATH = "/api/bot/webhook"


def webhook_url() -> str:
    if settings.TELEGRAM_WEBHOOK_URL:
        return settings.TELEGRAM_WEBHOOK_URL
    return settings.PUBLIC_SITE_URL.rstrip("/") + WEBHOOK_PATH


async def setup_bot() -> None:
    """Идемпотентно: ставим menu button и webhook. Требуется https (Telegram)."""
    if not settings.BOT_TOKEN:
        log.info("BOT_TOKEN не задан — настройка бота пропущена")
        return

    bot = get_bot()
    site = settings.PUBLIC_SITE_URL

    # Кнопка-меню бота → открывает Mini App (замена кнопки DIKIDI).
    if site.startswith("https://"):
        try:
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    text="Записаться", web_app=WebAppInfo(url=site)
                )
            )
            log.info("Menu button (web_app) установлена")
        except Exception:
            log.exception("Не удалось поставить menu button")

    # Webhook (только по https — Telegram иначе не примет).
    url = webhook_url()
    if url.startswith("https://"):
        try:
            await bot.set_webhook(
                url=url,
                secret_token=settings.TELEGRAM_WEBHOOK_SECRET or None,
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True,
            )
            log.info("Webhook установлен: %s", url)
        except Exception:
            log.exception("Не удалось установить webhook")
    else:
        log.info("PUBLIC_SITE_URL не https (%s) — webhook пропущен (dev)", site)
