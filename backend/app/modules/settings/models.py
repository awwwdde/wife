"""Master — мастер и его настройки.

Заложено на мультимастер (master_id везде), но UI/логика Фазы 1 — под одного.
Приватные/настроечные поля из DECISIONS §5: address, slot_step_min, cancellation_hours.
"""

from datetime import time

from sqlalchemy import Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings as app_settings
from app.database.base import Base, PKMixin, TimestampMixin


class Master(Base, PKMixin, TimestampMixin):
    __tablename__ = "master"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32))
    timezone: Mapped[str] = mapped_column(String(64), default="Europe/Moscow")

    # Приватный адрес студии: отдаётся клиенту ТОЛЬКО после записи (DECISIONS §3).
    address: Mapped[str | None] = mapped_column(String(255))

    # Шаг сетки слотов, мин (мастер выставляет сам при построении графика).
    slot_step_min: Mapped[int] = mapped_column(Integer, default=30)

    # Отмена/перенос не позднее N часов до визита (дефолт из .env).
    cancellation_hours: Mapped[int] = mapped_column(
        Integer, default=app_settings.CANCELLATION_HOURS
    )

    # Дефолтное «рабочее» окно-подсказка (реальный график — в working_hours).
    default_day_start: Mapped[time | None] = mapped_column(Time)
    default_day_end: Mapped[time | None] = mapped_column(Time)
