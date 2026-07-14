"""Расчёт свободных слотов: WorkingHours − TimeOff − занятые Appointment.

Учитываются суммарная длительность выбранных услуг и буфер, шаг сетки мастера
(slot_step_min). Времена в БД — UTC; график задан в локальной зоне мастера.
"""

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.booking import repository as repo
from app.modules.settings.models import Master


def _overlaps(a0: datetime, a1: datetime, b0: datetime, b1: datetime) -> bool:
    return a0 < b1 and b0 < a1


async def compute_slots(
    session: AsyncSession,
    master: Master,
    day: date,
    needed_min: int,
    buffer_min: int,
) -> list[datetime]:
    """Список стартов свободных слотов (UTC) на указанный день."""
    tz = ZoneInfo(master.timezone)
    wh = await repo.get_working_hours(session, master.id, day.weekday())
    if wh is None or wh.is_day_off or wh.start_time is None or wh.end_time is None:
        return []

    work_start = datetime.combine(day, wh.start_time, tzinfo=tz).astimezone(UTC)
    work_end = datetime.combine(day, wh.end_time, tzinfo=tz).astimezone(UTC)

    needed = timedelta(minutes=needed_min)
    buf = timedelta(minutes=buffer_min)
    step = timedelta(minutes=master.slot_step_min or 30)

    appts = await repo.get_active_appointments(session, master.id, work_start, work_end)
    timeoffs = await repo.get_timeoffs(session, master.id, work_start, work_end)
    busy = [(a.start_at, a.end_at) for a in appts] + [
        (t.start_at, t.end_at) for t in timeoffs
    ]

    now = datetime.now(UTC)
    slots: list[datetime] = []
    cursor = work_start
    while cursor + needed <= work_end:
        cand_start, cand_end = cursor, cursor + needed
        if cand_start >= now:
            # Буфер — как зазор вокруг кандидата от занятых интервалов.
            free = all(
                not _overlaps(cand_start - buf, cand_end + buf, b0, b1) for b0, b1 in busy
            )
            if free:
                slots.append(cand_start)
        cursor += step
    return slots
