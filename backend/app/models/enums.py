"""Строковые enum'ы домена. Значения совпадают с SPEC §5 / DECISIONS §5."""

import enum


class AppointmentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"


class AppointmentSource(str, enum.Enum):
    site = "site"
    miniapp = "miniapp"
    bot = "bot"
    manual = "manual"


class ReminderType(str, enum.Enum):
    confirmation = "confirmation"
    day_before = "day_before"
    hours_before = "hours_before"
    review_request = "review_request"


class ReminderStatus(str, enum.Enum):
    scheduled = "scheduled"
    sent = "sent"
    failed = "failed"


class ReviewStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
