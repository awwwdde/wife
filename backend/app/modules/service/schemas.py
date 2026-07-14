"""Pydantic-схемы услуги (публичная витрина)."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    duration_min: int
    price: Decimal
    category: str | None
    photo_url: str | None
