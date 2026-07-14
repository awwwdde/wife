"""Доступ к данным услуг. Бизнес-логику держим в сервисах/репозиториях, не в роутерах."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.service.models import Service


async def list_active_services(session: AsyncSession) -> list[Service]:
    result = await session.execute(
        select(Service).where(Service.is_active.is_(True)).order_by(Service.id)
    )
    return list(result.scalars().all())
