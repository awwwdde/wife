"""Старт-инициализация БД: демо-сид (мастер/услуги/график) + bootstrap-админ CRM.

Оба шага идемпотентны. Запуск: python -m app.scripts.seed
"""

import asyncio
from datetime import time
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.admin_security import (
    generate_totp_secret,
    hash_password,
    totp_provisioning_uri,
)
from app.core.config import settings
from app.database.session import async_session_maker
from app.models.admin import AdminUser
from app.models.working_hours import WorkingHours
from app.modules.service.models import Service
from app.modules.settings.models import Master


async def seed_demo(session: AsyncSession) -> None:
    existing = await session.execute(select(Master).limit(1))
    if existing.scalar_one_or_none():
        print("Демо-сид уже применён — пропускаю.")
        return

    master = Master(
        name="Ангелина",
        timezone="Europe/Moscow",
        address="Приватный адрес (виден только после записи)",
        slot_step_min=30,
    )
    session.add(master)
    await session.flush()

    session.add_all(
        [
            Service(
                master_id=master.id,
                title="Оформление и ламинирование бровей",
                description="Коррекция формы, окрашивание, долговременная укладка.",
                duration_min=90,
                buffer_min=15,
                price=Decimal("2500.00"),
                category="Брови",
            ),
            Service(
                master_id=master.id,
                title="Ламинирование ресниц",
                description="Завиток, объём и уход за ресницами без наращивания.",
                duration_min=75,
                buffer_min=15,
                price=Decimal("2200.00"),
                category="Ресницы",
            ),
        ]
    )
    for weekday in range(7):
        is_off = weekday == 6
        session.add(
            WorkingHours(
                master_id=master.id,
                weekday=weekday,
                start_time=None if is_off else time(10, 0),
                end_time=None if is_off else time(20, 0),
                is_day_off=is_off,
            )
        )
    await session.commit()
    print("Демо-сид применён: мастер Ангелина, 2 услуги, график Пн–Сб.")


async def bootstrap_admin(session: AsyncSession) -> None:
    email = settings.BOOTSTRAP_ADMIN_EMAIL.strip()
    password = settings.BOOTSTRAP_ADMIN_PASSWORD
    if not email or not password:
        print("BOOTSTRAP_ADMIN_* не заданы — админ не создаётся.")
        return

    result = await session.execute(select(AdminUser).where(AdminUser.email == email))
    admin = result.scalar_one_or_none()
    newly = False
    if admin is None:
        admin = AdminUser(email=email, password_hash=hash_password(password))
        session.add(admin)
        newly = True
    else:
        # env — источник истины: обновляем пароль (сброс через env).
        admin.password_hash = hash_password(password)

    if not admin.totp_secret:
        admin.totp_secret = generate_totp_secret()
        newly = True

    await session.commit()

    if newly:
        uri = totp_provisioning_uri(admin.totp_secret, email)
        print("=" * 60)
        print(f"CRM-админ готов: {email}")
        print("Добавьте 2FA в приложение-аутентификатор по ссылке (otpauth://):")
        print(uri)
        print("=" * 60)
    else:
        print(f"CRM-админ обновлён: {email} (пароль сброшен из env).")


async def main() -> None:
    async with async_session_maker() as session:
        await seed_demo(session)
        await bootstrap_admin(session)


if __name__ == "__main__":
    asyncio.run(main())
