"""Доступ к настройкам мастера. Пока один мастер (DECISIONS §2) — берём первого."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.settings.models import Master


async def get_default_master(session: AsyncSession) -> Master | None:
    result = await session.execute(select(Master).order_by(Master.id).limit(1))
    return result.scalar_one_or_none()
