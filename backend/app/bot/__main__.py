"""Каркас Telegram-бота (aiogram 3.x).

Фаза 1 — только скелет: без токена бот в polling-заглушке ничего не делает.
Фаза 3 наполнит: замена кнопки DIKIDI на Mini App, /start + request_contact,
инлайн-подтверждение/отмена, webhook на проде.
"""

import asyncio
import logging

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("askbrows.bot")


async def main() -> None:
    if not settings.BOT_TOKEN:
        log.warning(
            "BOT_TOKEN не задан — бот в режиме заглушки (ожидается на фазе 2–3). "
            "Процесс жив, но обработчиков нет."
        )
        # Держим процесс живым, чтобы контейнер не рестартовал в цикле.
        await asyncio.Event().wait()
        return

    # --- Реальная инициализация (фаза 3) ---
    from aiogram import Bot, Dispatcher

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # TODO(фаза 3): подключить хэндлеры (/start, request_contact, инлайн-кнопки).
    log.info("Бот запущен (polling для dev; на проде — webhook).")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
