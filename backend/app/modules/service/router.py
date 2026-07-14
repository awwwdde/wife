"""Публичные эндпоинты услуг (витрина тянет отсюда)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.service.repository import list_active_services
from app.modules.service.schemas import ServiceRead

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=list[ServiceRead])
async def get_services(session: AsyncSession = Depends(get_session)) -> list[ServiceRead]:
    services = await list_active_services(session)
    return [ServiceRead.model_validate(s) for s in services]
