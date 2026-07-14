"""Эндпоинты записи: слоты, создание, мои записи, отмена/перенос."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.auth.dependencies import get_current_client
from app.modules.booking import repository as repo
from app.modules.booking import service
from app.modules.booking.schemas import (
    AppointmentCreate,
    AppointmentRead,
    RescheduleRequest,
    SlotRead,
)
from app.modules.booking.slots import compute_slots
from app.modules.client.models import Client
from app.modules.settings.repository import get_default_master

router = APIRouter(tags=["booking"])


async def _require_master(session: AsyncSession):
    master = await get_default_master(session)
    if master is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "master is not configured (run seed)")
    return master


@router.get("/slots", response_model=list[SlotRead])
async def get_slots(
    day: date = Query(alias="date"),
    service_ids: list[int] = Query(),
    session: AsyncSession = Depends(get_session),
) -> list[SlotRead]:
    master = await _require_master(session)
    services = await repo.get_services_by_ids(session, master.id, service_ids)
    if len(services) != len(set(service_ids)):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "some services not found")
    needed_min = sum(s.duration_min for s in services)
    buffer_min = sum(s.buffer_min for s in services)
    starts = await compute_slots(session, master, day, needed_min, buffer_min)
    return [SlotRead(start_at=s) for s in starts]


@router.post("/appointments", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    data: AppointmentCreate,
    client: Client = Depends(get_current_client),
    session: AsyncSession = Depends(get_session),
) -> AppointmentRead:
    master = await _require_master(session)
    appt = await service.create_appointment(session, client, master, data)
    return AppointmentRead.model_validate(appt)


@router.get("/appointments/my", response_model=list[AppointmentRead])
async def my_appointments(
    client: Client = Depends(get_current_client),
    session: AsyncSession = Depends(get_session),
) -> list[AppointmentRead]:
    appts = await repo.list_client_appointments(session, client.id)
    return [AppointmentRead.model_validate(a) for a in appts]


async def _load_owned(session: AsyncSession, appointment_id: int, client: Client):
    appt = await repo.get_client_appointment(session, appointment_id, client.id)
    if appt is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "appointment not found")
    return appt


@router.post("/appointments/{appointment_id}/cancel", response_model=AppointmentRead)
async def cancel(
    appointment_id: int,
    client: Client = Depends(get_current_client),
    session: AsyncSession = Depends(get_session),
) -> AppointmentRead:
    appt = await _load_owned(session, appointment_id, client)
    appt = await service.cancel_appointment(session, appt)
    return AppointmentRead.model_validate(appt)


@router.post("/appointments/{appointment_id}/reschedule", response_model=AppointmentRead)
async def reschedule(
    appointment_id: int,
    payload: RescheduleRequest,
    client: Client = Depends(get_current_client),
    session: AsyncSession = Depends(get_session),
) -> AppointmentRead:
    appt = await _load_owned(session, appointment_id, client)
    appt = await service.reschedule_appointment(session, appt, payload.start_at)
    return AppointmentRead.model_validate(appt)
