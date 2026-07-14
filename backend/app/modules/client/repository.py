"""Доступ к данным клиентов."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.telegram_auth import TelegramUser
from app.modules.client.models import Client


async def get_by_id(session: AsyncSession, client_id: int) -> Client | None:
    return await session.get(Client, client_id)


async def get_by_telegram_id(session: AsyncSession, telegram_id: int) -> Client | None:
    result = await session.execute(select(Client).where(Client.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_or_create_by_telegram(session: AsyncSession, tg: TelegramUser) -> Client:
    result = await session.execute(select(Client).where(Client.telegram_id == tg.id))
    client = result.scalar_one_or_none()
    if client is None:
        client = Client(telegram_id=tg.id)
        session.add(client)
    # Обновляем профиль из Telegram при каждом входе.
    client.first_name = tg.first_name
    client.last_name = tg.last_name
    client.username = tg.username
    if tg.photo_url:
        client.photo_url = tg.photo_url
    await session.flush()
    return client


async def set_phone(session: AsyncSession, client: Client, phone: str) -> None:
    client.phone = phone
    await session.flush()


async def set_consent(session: AsyncSession, client: Client) -> None:
    if client.consent_at is None:
        client.consent_at = datetime.now(UTC)
        await session.flush()
