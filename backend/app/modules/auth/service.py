"""Логика авторизации: валидная TG-подпись → Client → JWT."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.core.telegram_auth import TelegramUser
from app.modules.client import repository as client_repo
from app.modules.client.models import Client


async def authenticate(session: AsyncSession, tg: TelegramUser) -> tuple[Client, str]:
    """Найти/создать клиента по данным Telegram и выпустить токен."""
    client = await client_repo.get_or_create_by_telegram(session, tg)
    await session.commit()
    token = create_access_token(client.id)
    return client, token
