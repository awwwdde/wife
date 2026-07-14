"""Client — клиент. Телефон заполняет бот через request_contact.

consent_at — факт согласия на обработку ПДн (152-ФЗ, DECISIONS §5/§7).
"""

from datetime import datetime

from sqlalchemy import ARRAY, BigInteger, Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, PKMixin, TimestampMixin


class Client(Base, PKMixin, TimestampMixin):
    __tablename__ = "client"

    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String(120))
    last_name: Mapped[str | None] = mapped_column(String(120))
    username: Mapped[str | None] = mapped_column(String(120))

    # Телефон — ПДн; получаем через request_contact (бот) или requestContact (Mini App).
    phone: Mapped[str | None] = mapped_column(String(32), index=True)
    photo_url: Mapped[str | None] = mapped_column(String(512))

    # Приватные заметки мастера + теги для сегментации рассылок.
    notes: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)

    # Факт согласия на обработку ПДн (nullable — до первой записи).
    consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
