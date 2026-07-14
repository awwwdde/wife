"""Единая точка импорта всех моделей.

Alembic autogenerate и создание схемы опираются на Base.metadata — поэтому
все модели должны быть импортированы здесь (иначе таблицы «не видны»).
"""

from app.database.base import Base
from app.models.appointment import Appointment, appointment_services
from app.models.reminder import Reminder
from app.models.review import Review
from app.models.timeoff import TimeOff
from app.models.working_hours import WorkingHours
from app.modules.client.models import Client
from app.modules.service.models import Service
from app.modules.settings.models import Master

__all__ = [
    "Base",
    "Master",
    "Client",
    "Service",
    "Appointment",
    "appointment_services",
    "WorkingHours",
    "TimeOff",
    "Reminder",
    "Review",
]
