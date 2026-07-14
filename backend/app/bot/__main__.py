"""Локальный запуск бота в режиме polling (для dev без публичного домена).

На проде/панели бот работает через webhook внутри веб-приложения (см. app/bot/webhook.py),
этот entrypoint для docker-compose и локальной отладки.
"""

import asyncio
import logging

from app.bot import get_bot, get_dispatcher
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("askbrows.bot")


async def main() -> None:
    if not settings.BOT_TOKEN:
        log.warning("BOT_TOKEN не задан — бот-заглушка, обработчиков нет.")
        await asyncio.Event().wait()
        return

    bot = get_bot()
    dp = get_dispatcher()
    # В polling убираем webhook, чтобы не конфликтовал.
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Бот запущен (polling, dev).")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
