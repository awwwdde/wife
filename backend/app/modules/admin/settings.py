"""Настройки мастера (CRM): имя, приватный адрес, шаг слота, часы отмены."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.admin.dependencies import get_current_admin
from app.modules.settings.models import Master
from app.modules.settings.repository import get_default_master

router = APIRouter(
    prefix="/admin/settings",
    tags=["admin-settings"],
    dependencies=[Depends(get_current_admin)],
)


class MasterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str | None
    timezone: str
    address: str | None
    slot_step_min: int
    cancellation_hours: int


class MasterUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    timezone: str | None = None
    address: str | None = None
    slot_step_min: int | None = None
    cancellation_hours: int | None = None


@router.get("", response_model=MasterRead)
async def get_settings(session: AsyncSession = Depends(get_session)) -> Master:
    master = await get_default_master(session)
    if master is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "master is not configured")
    return master


@router.patch("", response_model=MasterRead)
async def update_settings(
    data: MasterUpdate, session: AsyncSession = Depends(get_session)
) -> Master:
    master = await get_default_master(session)
    if master is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "master is not configured")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(master, field, value)
    await session.commit()
    await session.refresh(master)
    return master
