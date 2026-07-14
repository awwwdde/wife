"""Записи в CRM: календарь (диапазон), ручная запись, смена статуса (исход)."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.models.appointment import Appointment
from app.models.enums import AppointmentSource, AppointmentStatus
from app.modules.admin.dependencies import get_current_admin
from app.modules.booking import repository as booking_repo
from app.modules.client.models import Client
from app.modules.settings.repository import get_default_master

router = APIRouter(
    prefix="/admin/appointments",
    tags=["admin-appointments"],
    dependencies=[Depends(get_current_admin)],
)


class NewClient(BaseModel):
    first_name: str
    phone: str | None = None


class AppointmentAdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_at: datetime
    end_at: datetime
    status: AppointmentStatus
    source: AppointmentSource
    comment: str | None
    client_id: int
    client_name: str | None
    client_phone: str | None
    services: list[str]


class ManualCreate(BaseModel):
    service_ids: list[int] = Field(min_length=1)
    start_at: datetime
    comment: str | None = None
    client_id: int | None = None
    new_client: NewClient | None = None


class StatusUpdate(BaseModel):
    status: AppointmentStatus


def _to_read(appt: Appointment, client: Client | None) -> AppointmentAdminRead:
    name = None
    if client:
        name = " ".join(filter(None, [client.first_name, client.last_name])) or client.username
    return AppointmentAdminRead(
        id=appt.id,
        start_at=appt.start_at,
        end_at=appt.end_at,
        status=appt.status,
        source=appt.source,
        comment=appt.comment,
        client_id=appt.client_id,
        client_name=name,
        client_phone=client.phone if client else None,
        services=[s.title for s in appt.services],
    )


@router.get("", response_model=list[AppointmentAdminRead])
async def list_appointments(
    date_from: datetime = Query(alias="from"),
    date_to: datetime = Query(alias="to"),
    session: AsyncSession = Depends(get_session),
) -> list[AppointmentAdminRead]:
    result = await session.execute(
        select(Appointment)
        .where(Appointment.start_at >= date_from, Appointment.start_at < date_to)
        .order_by(Appointment.start_at)
    )
    appts = list(result.scalars().all())
    out: list[AppointmentAdminRead] = []
    for a in appts:
        client = await session.get(Client, a.client_id)
        out.append(_to_read(a, client))
    return out


@router.post("", response_model=AppointmentAdminRead, status_code=status.HTTP_201_CREATED)
async def create_manual(
    data: ManualCreate, session: AsyncSession = Depends(get_session)
) -> AppointmentAdminRead:
    master = await get_default_master(session)
    if master is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "master is not configured")

    # Клиент: существующий или новый (запись «с улицы» / по телефону).
    if data.client_id is not None:
        client = await session.get(Client, data.client_id)
        if client is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "client not found")
    elif data.new_client is not None:
        client = Client(
            first_name=data.new_client.first_name, phone=data.new_client.phone
        )
        session.add(client)
        await session.flush()
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "client_id or new_client required")

    services = await booking_repo.get_services_by_ids(session, master.id, data.service_ids)
    if len(services) != len(set(data.service_ids)):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "some services not found")

    start_at = data.start_at
    if start_at.tzinfo is None:
        start_at = start_at.replace(tzinfo=UTC)
    total_min = sum(s.duration_min for s in services)

    appt = Appointment(
        master_id=master.id,
        client_id=client.id,
        start_at=start_at,
        end_at=start_at + timedelta(minutes=total_min),
        status=AppointmentStatus.confirmed,  # ручная запись сразу подтверждена
        source=AppointmentSource.manual,
        comment=data.comment,
    )
    appt.services = services
    session.add(appt)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "slot is already taken") from exc
    await session.commit()
    return _to_read(appt, client)


@router.patch("/{appointment_id}/status", response_model=AppointmentAdminRead)
async def set_status(
    appointment_id: int,
    data: StatusUpdate,
    session: AsyncSession = Depends(get_session),
) -> AppointmentAdminRead:
    appt = await session.get(Appointment, appointment_id)
    if appt is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "appointment not found")
    appt.status = data.status
    await session.commit()
    client = await session.get(Client, appt.client_id)
    return _to_read(appt, client)
