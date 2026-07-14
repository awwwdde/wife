from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AppointmentSource, AppointmentStatus


class SlotRead(BaseModel):
    start_at: datetime  # UTC


class ServiceBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    duration_min: int
    price: Decimal


class AppointmentCreate(BaseModel):
    service_ids: list[int] = Field(min_length=1)
    start_at: datetime  # UTC ISO
    comment: str | None = None
    consent: bool  # согласие на обработку ПДн (152-ФЗ) — обязательно True
    source: AppointmentSource = AppointmentSource.site


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_at: datetime
    end_at: datetime
    status: AppointmentStatus
    comment: str | None
    services: list[ServiceBrief]


class RescheduleRequest(BaseModel):
    start_at: datetime  # новый старт, UTC
