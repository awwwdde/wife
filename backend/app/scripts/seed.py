"""Демо-сид: мастер + пара услуг + недельный график.

Нужен, чтобы тестировать витрину/запись до готовой админки (DECISIONS §3).
Запуск: python -m app.scripts.seed
"""

import asyncio
from datetime import time
from decimal import Decimal

from sqlalchemy import select

from app.database.session import async_session_maker
from app.models.working_hours import WorkingHours
from app.modules.service.models import Service
from app.modules.settings.models import Master


async def seed() -> None:
    async with async_session_maker() as session:
        existing = await session.execute(select(Master).limit(1))
        if existing.scalar_one_or_none():
            print("Сид уже применён — пропускаю.")
            return

        master = Master(
            name="Ангелина",
            timezone="Europe/Moscow",
            address="Приватный адрес (виден только после записи)",
            slot_step_min=30,
        )
        session.add(master)
        await session.flush()  # получить master.id

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

        # График: Пн–Сб 10:00–20:00, Вс выходной.
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


if __name__ == "__main__":
    asyncio.run(seed())
