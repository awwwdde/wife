"""WorkingHours — недельный график работы мастера (weekday 0=Пн … 6=Вс)."""

from datetime import time

from sqlalchemy import Boolean, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, PKMixin


class WorkingHours(Base, PKMixin):
    __tablename__ = "working_hours"

    master_id: Mapped[int] = mapped_column(
        ForeignKey("master.id", ondelete="CASCADE"), index=True
    )
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)  # 0..6
    start_time: Mapped[time | None] = mapped_column(Time)
    end_time: Mapped[time | None] = mapped_column(Time)
    is_day_off: Mapped[bool] = mapped_column(Boolean, default=False)
