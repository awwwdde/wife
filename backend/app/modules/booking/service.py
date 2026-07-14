"""Создание/отмена/перенос записи с защитой от двойного бронирования."""

from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus, ReminderStatus, ReminderType
from app.models.reminder import Reminder
from app.modules.booking import repository as repo
from app.modules.booking.schemas import AppointmentCreate
from app.modules.client import repository as client_repo
from app.modules.client.models import Client
from app.modules.settings.models import Master


def _schedule_reminders(session: AsyncSession, appt: Appointment) -> None:
    """Заготовить строки напоминаний (отправит воркер/бот в Фазе 3)."""
    now = datetime.now(UTC)
    planned: list[tuple[ReminderType, datetime]] = [
        (ReminderType.confirmation, now),
        (ReminderType.day_before, appt.start_at - timedelta(hours=24)),
        (ReminderType.hours_before, appt.start_at - timedelta(hours=2)),
        (ReminderType.review_request, appt.end_at + timedelta(hours=1)),
    ]
    for r_type, send_at in planned:
        # Прошедшие моменты (кроме подтверждения) не планируем.
        if r_type is not ReminderType.confirmation and send_at <= now:
            continue
        session.add(
            Reminder(
                appointment_id=appt.id,
                type=r_type,
                send_at=send_at,
                status=ReminderStatus.scheduled,
            )
        )


async def _drop_scheduled_reminders(session: AsyncSession, appointment_id: int) -> None:
    await session.execute(
        delete(Reminder).where(
            Reminder.appointment_id == appointment_id,
            Reminder.status == ReminderStatus.scheduled,
        )
    )


async def create_appointment(
    session: AsyncSession, client: Client, master: Master, data: AppointmentCreate
) -> Appointment:
    if not data.consent:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "consent is required")

    services = await repo.get_services_by_ids(session, master.id, data.service_ids)
    if len(services) != len(set(data.service_ids)):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "some services not found")

    total_min = sum(s.duration_min for s in services)
    start_at = data.start_at
    if start_at.tzinfo is None:
        start_at = start_at.replace(tzinfo=UTC)
    if start_at <= datetime.now(UTC):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "start_at must be in the future")
    end_at = start_at + timedelta(minutes=total_min)

    await client_repo.set_consent(session, client)

    appt = Appointment(
        master_id=master.id,
        client_id=client.id,
        start_at=start_at,
        end_at=end_at,
        status=AppointmentStatus.pending,
        source=data.source,
        comment=data.comment,
    )
    appt.services = services
    session.add(appt)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        # Сработал EXCLUDE-констрейнт — слот уже занят.
        raise HTTPException(status.HTTP_409_CONFLICT, "slot is already taken") from exc

    _schedule_reminders(session, appt)
    await session.commit()
    # Не вызываем refresh: expire_on_commit=False, а appt.services уже наполнен
    # объектами Service (иначе ленивая загрузка в sync-сериализации → MissingGreenlet).
    return appt


def _ensure_cancellable(appt: Appointment) -> None:
    if appt.status not in (AppointmentStatus.pending, AppointmentStatus.confirmed):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "appointment is not active")
    deadline = appt.start_at - timedelta(hours=settings.CANCELLATION_HOURS)
    if datetime.now(UTC) > deadline:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"changes are allowed no later than {settings.CANCELLATION_HOURS}h before",
        )


async def cancel_appointment(session: AsyncSession, appt: Appointment) -> Appointment:
    _ensure_cancellable(appt)
    appt.status = AppointmentStatus.cancelled
    await _drop_scheduled_reminders(session, appt.id)
    await session.commit()
    return appt


async def reschedule_appointment(
    session: AsyncSession, appt: Appointment, new_start: datetime
) -> Appointment:
    _ensure_cancellable(appt)
    if new_start.tzinfo is None:
        new_start = new_start.replace(tzinfo=UTC)
    if new_start <= datetime.now(UTC):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "start_at must be in the future")

    duration = appt.end_at - appt.start_at
    appt.start_at = new_start
    appt.end_at = new_start + duration
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "slot is already taken") from exc

    await _drop_scheduled_reminders(session, appt.id)
    _schedule_reminders(session, appt)
    await session.commit()
    return appt
