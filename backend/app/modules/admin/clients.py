"""База клиентов (CRM): список и карточка с историей."""

from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.modules.admin.dependencies import get_current_admin
from app.modules.client.models import Client

router = APIRouter(
    prefix="/admin/clients",
    tags=["admin-clients"],
    dependencies=[Depends(get_current_admin)],
)


class ClientListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str | None
    last_name: str | None
    username: str | None
    phone: str | None
    telegram_id: int | None


class AppointmentBrief(BaseModel):
    id: int
    start_at: datetime
    status: AppointmentStatus
    services: list[str]
    total: Decimal


class ClientDetail(ClientListItem):
    notes: str | None
    tags: list[str] | None
    consent_at: datetime | None
    visits: int
    total_spent: Decimal
    appointments: list[AppointmentBrief]


@router.get("", response_model=list[ClientListItem])
async def list_clients(
    q: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[Client]:
    stmt = select(Client).order_by(Client.id.desc())
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                Client.first_name.ilike(like),
                Client.last_name.ilike(like),
                Client.phone.ilike(like),
                Client.username.ilike(like),
            )
        )
    result = await session.execute(stmt.limit(200))
    return list(result.scalars().all())


@router.get("/{client_id}", response_model=ClientDetail)
async def client_detail(
    client_id: int, session: AsyncSession = Depends(get_session)
) -> ClientDetail:
    client = await session.get(Client, client_id)
    if client is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "client not found")

    result = await session.execute(
        select(Appointment)
        .where(Appointment.client_id == client_id)
        .order_by(Appointment.start_at.desc())
    )
    appts = list(result.scalars().all())

    briefs: list[AppointmentBrief] = []
    total_spent = Decimal("0")
    visits = 0
    for a in appts:
        total = sum((s.price for s in a.services), Decimal("0"))
        if a.status == AppointmentStatus.completed:
            visits += 1
            total_spent += total
        briefs.append(
            AppointmentBrief(
                id=a.id,
                start_at=a.start_at,
                status=a.status,
                services=[s.title for s in a.services],
                total=total,
            )
        )

    return ClientDetail(
        id=client.id,
        first_name=client.first_name,
        last_name=client.last_name,
        username=client.username,
        phone=client.phone,
        telegram_id=client.telegram_id,
        notes=client.notes,
        tags=client.tags,
        consent_at=client.consent_at,
        visits=visits,
        total_spent=total_spent,
        appointments=briefs,
    )
