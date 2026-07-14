"""CRUD услуг (CRM)."""

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.admin.dependencies import get_current_admin
from app.modules.service.models import Service
from app.modules.settings.repository import get_default_master

router = APIRouter(
    prefix="/admin/services",
    tags=["admin-services"],
    dependencies=[Depends(get_current_admin)],
)


class ServiceAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    duration_min: int
    buffer_min: int
    price: Decimal
    deposit_amount: Decimal | None
    category: str | None
    photo_url: str | None
    is_active: bool


class ServiceCreate(BaseModel):
    title: str
    description: str | None = None
    duration_min: int
    buffer_min: int = 0
    price: Decimal
    deposit_amount: Decimal | None = None
    category: str | None = None
    photo_url: str | None = None
    is_active: bool = True


class ServiceUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    duration_min: int | None = None
    buffer_min: int | None = None
    price: Decimal | None = None
    deposit_amount: Decimal | None = None
    category: str | None = None
    photo_url: str | None = None
    is_active: bool | None = None


@router.get("", response_model=list[ServiceAdminRead])
async def list_services(session: AsyncSession = Depends(get_session)) -> list[Service]:
    result = await session.execute(select(Service).order_by(Service.id))
    return list(result.scalars().all())


@router.post("", response_model=ServiceAdminRead, status_code=status.HTTP_201_CREATED)
async def create_service(
    data: ServiceCreate, session: AsyncSession = Depends(get_session)
) -> Service:
    master = await get_default_master(session)
    if master is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "master is not configured")
    service = Service(master_id=master.id, **data.model_dump())
    session.add(service)
    await session.commit()
    await session.refresh(service)
    return service


@router.patch("/{service_id}", response_model=ServiceAdminRead)
async def update_service(
    service_id: int, data: ServiceUpdate, session: AsyncSession = Depends(get_session)
) -> Service:
    service = await session.get(Service, service_id)
    if service is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "service not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(service, field, value)
    await session.commit()
    await session.refresh(service)
    return service


@router.delete("/{service_id}")
async def delete_service(
    service_id: int, session: AsyncSession = Depends(get_session)
) -> dict[str, bool]:
    service = await session.get(Service, service_id)
    if service is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "service not found")
    # Мягкое удаление — сохраняем историю записей.
    service.is_active = False
    await session.commit()
    return {"ok": True}
