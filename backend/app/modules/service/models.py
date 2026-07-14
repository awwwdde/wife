"""Service — услуга. buffer_min добавлен по DECISIONS §5 (влияет на расчёт слотов)."""

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, PKMixin


class Service(Base, PKMixin):
    __tablename__ = "service"

    master_id: Mapped[int] = mapped_column(
        ForeignKey("master.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    duration_min: Mapped[int] = mapped_column(Integer, nullable=False)
    # Буфер после услуги (уборка/подготовка) — учитывается при построении слотов.
    buffer_min: Mapped[int] = mapped_column(Integer, default=0)

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    # Депозит оставлен на будущее (онлайн-оплаты в первом релизе нет, DECISIONS §2).
    deposit_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    category: Mapped[str | None] = mapped_column(String(80))
    photo_url: Mapped[str | None] = mapped_column(String(512))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
