"""Приём обновлений Telegram по webhook и передача в Dispatcher."""

import logging

from aiogram.types import Update
from fastapi import APIRouter, HTTPException, Request, status

from app.bot import get_bot, get_dispatcher
from app.core.config import settings

log = logging.getLogger("askbrows.bot")
router = APIRouter(prefix="/bot", tags=["bot"])


@router.post("/webhook")
async def telegram_webhook(request: Request) -> dict[str, bool]:
    # Проверка секрета (Telegram шлёт его в заголовке при set_webhook с secret_token).
    if settings.TELEGRAM_WEBHOOK_SECRET:
        got = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if got != settings.TELEGRAM_WEBHOOK_SECRET:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "bad secret")

    data = await request.json()
    bot = get_bot()
    update = Update.model_validate(data, context={"bot": bot})
    try:
        await get_dispatcher().feed_update(bot, update)
    except Exception:
        # Не отдаём 500 Telegram'у — иначе он будет ретраить; логируем и подтверждаем.
        log.exception("Ошибка обработки update")
    return {"ok": True}
