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
        _bot = Bot(token=settings.BOT_TOKEN)
    return _bot


def get_dispatcher() -> Dispatcher:
    global _dp
    if _dp is None:
        _dp = Dispatcher()
        from app.bot.handlers import router

        _dp.include_router(router)
    return _dp
