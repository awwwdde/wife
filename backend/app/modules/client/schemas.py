from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int | None
    first_name: str | None
    last_name: str | None
    username: str | None
    phone: str | None
    consent_at: datetime | None


class PhoneUpdate(BaseModel):
    phone: str
