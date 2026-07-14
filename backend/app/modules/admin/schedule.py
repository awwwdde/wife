"""График работы (WorkingHours) и отпуска/перерывы (TimeOff) в CRM."""

from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.models.timeoff import TimeOff
from app.models.working_hours import WorkingHours
from app.modules.admin.dependencies import get_current_admin
from app.modules.settings.repository import get_default_master

router = APIRouter(
    prefix="/admin",
    tags=["admin-schedule"],
    dependencies=[Depends(get_current_admin)],
)


class WorkingHoursItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    weekday: int  # 0=Пн … 6=Вс
    start_time: time | None = None
    end_time: time | None = None
    is_day_off: bool = False


class TimeOffRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_at: datetime
    end_at: datetime
    reason: str | None


class TimeOffCreate(BaseModel):
    start_at: datetime
    end_at: datetime
    reason: str | None = None


async def _require_master(session: AsyncSession):
    master = await get_default_master(session)
    if master is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "master is not configured")
    return master


@router.get("/schedule", response_model=list[WorkingHoursItem])
async def get_schedule(session: AsyncSession = Depends(get_session)) -> list[WorkingHours]:
    master = await _require_master(session)
    result = await session.execute(
        select(WorkingHours)
        .where(WorkingHours.master_id == master.id)
        .order_by(WorkingHours.weekday)
    )
    return list(result.scalars().all())


@router.put("/schedule", response_model=list[WorkingHoursItem])
async def put_schedule(
    items: list[WorkingHoursItem], session: AsyncSession = Depends(get_session)
) -> list[WorkingHours]:
    master = await _require_master(session)
    result = await session.execute(
        select(WorkingHours).where(WorkingHours.master_id == master.id)
    )
    by_weekday = {wh.weekday: wh for wh in result.scalars().all()}
    for item in items:
        wh = by_weekday.get(item.weekday)
        if wh is None:
            wh = WorkingHours(master_id=master.id, weekday=item.weekday)
            session.add(wh)
        wh.start_time = item.start_time
        wh.end_time = item.end_time
        wh.is_day_off = item.is_day_off
    await session.commit()
    return await get_schedule(session)


@router.get("/timeoff", response_model=list[TimeOffRead])
async def list_timeoff(session: AsyncSession = Depends(get_session)) -> list[TimeOff]:
    master = await _require_master(session)
    result = await session.execute(
        select(TimeOff).where(TimeOff.master_id == master.id).order_by(TimeOff.start_at)
    )
    return list(result.scalars().all())


@router.post("/timeoff", response_model=TimeOffRead, status_code=status.HTTP_201_CREATED)
async def create_timeoff(
    data: TimeOffCreate, session: AsyncSession = Depends(get_session)
) -> TimeOff:
    master = await _require_master(session)
    off = TimeOff(master_id=master.id, **data.model_dump())
    session.add(off)
    await session.commit()
    await session.refresh(off)
    return off


@router.delete("/timeoff/{timeoff_id}")
async def delete_timeoff(
    timeoff_id: int, session: AsyncSession = Depends(get_session)
) -> dict[str, bool]:
    await session.execute(delete(TimeOff).where(TimeOff.id == timeoff_id))
    await session.commit()
    return {"ok": True}
