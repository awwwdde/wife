"""Выборки для расчёта слотов и работы с записями."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.models.timeoff import TimeOff
from app.models.working_hours import WorkingHours
from app.modules.service.models import Service

# Записи, которые реально занимают слот (не отменённые / не no_show).
ACTIVE_STATUSES = (
    AppointmentStatus.pending,
    AppointmentStatus.confirmed,
    AppointmentStatus.completed,
)


async def get_working_hours(
    session: AsyncSession, master_id: int, weekday: int
) -> WorkingHours | None:
    result = await session.execute(
        select(WorkingHours).where(
            WorkingHours.master_id == master_id,
            WorkingHours.weekday == weekday,
        )
    )
    return result.scalar_one_or_none()


async def get_services_by_ids(
    session: AsyncSession, master_id: int, service_ids: list[int]
) -> list[Service]:
    result = await session.execute(
        select(Service).where(
            Service.master_id == master_id,
            Service.id.in_(service_ids),
            Service.is_active.is_(True),
        )
    )
    return list(result.scalars().all())


async def get_active_appointments(
    session: AsyncSession, master_id: int, start: datetime, end: datetime
) -> list[Appointment]:
    result = await session.execute(
        select(Appointment).where(
            Appointment.master_id == master_id,
            Appointment.status.in_(ACTIVE_STATUSES),
            Appointment.start_at < end,
            Appointment.end_at > start,
        )
    )
    return list(result.scalars().all())


async def get_timeoffs(
    session: AsyncSession, master_id: int, start: datetime, end: datetime
) -> list[TimeOff]:
    result = await session.execute(
        select(TimeOff).where(
            TimeOff.master_id == master_id,
            TimeOff.start_at < end,
            TimeOff.end_at > start,
        )
    )
    return list(result.scalars().all())


async def get_client_appointment(
    session: AsyncSession, appointment_id: int, client_id: int
) -> Appointment | None:
    result = await session.execute(
        select(Appointment).where(
            Appointment.id == appointment_id,
            Appointment.client_id == client_id,
        )
    )
    return result.scalar_one_or_none()


async def list_client_appointments(
    session: AsyncSession, client_id: int
) -> list[Appointment]:
    result = await session.execute(
        select(Appointment)
        .where(Appointment.client_id == client_id)
        .order_by(Appointment.start_at.desc())
    )
    return list(result.scalars().all())
