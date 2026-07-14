"""AdminUser — учётка мастера для входа в CRM (отдельно от клиентов)."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, PKMixin, TimestampMixin


class AdminUser(Base, PKMixin, TimestampMixin):
    __tablename__ = "admin_user"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # Секрет TOTP (2FA). None → 2FA ещё не подключена (нужен provision).
    totp_secret: Mapped[str | None] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
