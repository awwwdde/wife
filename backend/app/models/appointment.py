"""Appointment — запись. Мультиуслуга: many-to-many с Service (DECISIONS §5).

Защита от двойного бронирования — Postgres EXCLUDE constraint на пересечение
интервалов одного мастера (btree_gist + tstzrange). Констрейнт задаётся в
миграции 0001 (ExcludeConstraint здесь для наглядности/autogenerate).
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Table,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, PKMixin, TimestampMixin
from app.models.enums import AppointmentSource, AppointmentStatus

# Связующая таблица «запись ↔ услуги» (длительность и цена суммируются в сервисе).
appointment_services = Table(
    "appointment_services",
    Base.metadata,
    Column(
        "appointment_id",
        ForeignKey("appointment.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "service_id",
        ForeignKey("service.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)


class Appointment(Base, PKMixin, TimestampMixin):
    __tablename__ = "appointment"

    master_id: Mapped[int] = mapped_column(
        ForeignKey("master.id", ondelete="CASCADE"), index=True
    )
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id", ondelete="RESTRICT"))

    # Все времена в UTC. Отображение — Europe/Moscow.
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    status: Mapped[AppointmentStatus] = mapped_column(default=AppointmentStatus.pending)
    source: Mapped[AppointmentSource] = mapped_column(default=AppointmentSource.site)

    comment: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=lambda: datetime.utcnow()
    )

    services: Mapped[list["Service"]] = relationship(  # noqa: F821
        secondary=appointment_services, lazy="selectin"
    )

    __table_args__ = (
        # Нет двух пересекающихся активных записей у одного мастера.
        # Отменённые/no_show интервалы исключены из проверки (освобождают слот).
        ExcludeConstraint(
            (master_id, "="),
            (text("tstzrange(start_at, end_at)"), "&&"),
            name="appointment_no_overlap",
            using="gist",
            where=text("status NOT IN ('cancelled', 'no_show')"),
        ),
    )
