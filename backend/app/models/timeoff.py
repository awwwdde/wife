"""TimeOff — отпуска/перерывы/выходные вне регулярного графика."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, PKMixin


class TimeOff(Base, PKMixin):
    __tablename__ = "time_off"

    master_id: Mapped[int] = mapped_column(
        ForeignKey("master.id", ondelete="CASCADE"), index=True
    )
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255))
