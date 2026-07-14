"""Reminder — запланированное уведомление.

Модель отправки (DECISIONS §2): таблица + воркер раз/мин сканирует
status='scheduled' AND send_at<=now(). Идемпотентность через sent_at.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, PKMixin
from app.models.enums import ReminderStatus, ReminderType


class Reminder(Base, PKMixin):
    __tablename__ = "reminder"

    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointment.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[ReminderType] = mapped_column(nullable=False)
    send_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[ReminderStatus] = mapped_column(default=ReminderStatus.scheduled)

    __table_args__ = (
        # Индекс под скан воркера: status + send_at.
        Index("ix_reminder_status_send_at", "status", "send_at"),
    )
