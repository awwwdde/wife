"""Общий Bot и Dispatcher (используются и webhook-роутом, и воркером)."""

from aiogram import Bot, Dispatcher

from app.core.config import settings

_bot: Bot | None = None
_dp: Dispatcher | None = None


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        if not settings.BOT_TOKEN:
            raise RuntimeError("BOT_TOKEN не задан")
        _bot = Bot(token=settings.BOT_TOKEN, session=_build_session())
    return _bot


def _build_session():
    """Сессия бота: свой Bot API base (реверс-прокси) или обычный прокси, иначе дефолт."""
    # Приоритет — собственный base-URL Bot API (напр. Cloudflare Worker):
    # обходит блокировку исходящего доступа к api.telegram.org.
    if settings.TELEGRAM_API_BASE:
        from aiogram.client.session.aiohttp import AiohttpSession
        from aiogram.client.telegram import TelegramAPIServer

        api = TelegramAPIServer.from_base(settings.TELEGRAM_API_BASE.rstrip("/"))
        return AiohttpSession(api=api)
    if settings.TELEGRAM_PROXY:
        from aiogram.client.session.aiohttp import AiohttpSession

        return AiohttpSession(proxy=settings.TELEGRAM_PROXY)
    return None


def get_dispatcher() -> Dispatcher:
    global _dp
    if _dp is None:
        _dp = Dispatcher()
        from app.bot.handlers import router

        _dp.include_router(router)
    return _dp
