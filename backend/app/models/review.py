"""Review — отзыв. Сбор через бота → модерация мастером → публикация (DECISIONS §2)."""

from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, PKMixin, TimestampMixin
from app.models.enums import ReviewStatus


class Review(Base, PKMixin, TimestampMixin):
    __tablename__ = "review"

    client_id: Mapped[int] = mapped_column(ForeignKey("client.id", ondelete="CASCADE"))
    appointment_id: Mapped[int | None] = mapped_column(
        ForeignKey("appointment.id", ondelete="SET NULL")
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..5
    text: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ReviewStatus] = mapped_column(default=ReviewStatus.pending)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
