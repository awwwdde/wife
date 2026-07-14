"""init schema (askbrows Фаза 1)

Revision ID: 0001_init
Revises:
Create Date: 2026-07-14

Полная схема из SPEC §5 + правки DECISIONS §5:
Appointment↔Service many-to-many, Service.buffer_min, Review,
приватный address / slot_step_min / cancellation_hours у Master, Client.consent_at.
Защита от двойного бронирования — EXCLUDE constraint (btree_gist + tstzrange).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_init"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# create_type=False: типы создаём/удаляем явно ниже, чтобы CREATE TABLE их не дублировал.
appointment_status = postgresql.ENUM(
    "pending", "confirmed", "completed", "cancelled", "no_show",
    name="appointmentstatus", create_type=False,
)
appointment_source = postgresql.ENUM(
    "site", "miniapp", "bot", "manual", name="appointmentsource", create_type=False,
)
reminder_type = postgresql.ENUM(
    "confirmation", "day_before", "hours_before", "review_request",
    name="remindertype", create_type=False,
)
reminder_status = postgresql.ENUM(
    "scheduled", "sent", "failed", name="reminderstatus", create_type=False,
)
review_status = postgresql.ENUM(
    "pending", "approved", "rejected", name="reviewstatus", create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()

    # Расширение для EXCLUDE-констрейнта (= по master_id, && по tstzrange).
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    for enum in (
        appointment_status, appointment_source,
        reminder_type, reminder_status, review_status,
    ):
        enum.create(bind, checkfirst=True)

    op.create_table(
        "master",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("phone", sa.String(32)),
        sa.Column("timezone", sa.String(64), server_default="Europe/Moscow"),
        sa.Column("address", sa.String(255)),
        sa.Column("slot_step_min", sa.Integer(), server_default="30"),
        sa.Column("cancellation_hours", sa.Integer(), server_default="6"),
        sa.Column("default_day_start", sa.Time()),
        sa.Column("default_day_end", sa.Time()),
    )

    op.create_table(
        "client",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("telegram_id", sa.BigInteger()),
        sa.Column("first_name", sa.String(120)),
        sa.Column("last_name", sa.String(120)),
        sa.Column("username", sa.String(120)),
        sa.Column("phone", sa.String(32)),
        sa.Column("photo_url", sa.String(512)),
        sa.Column("notes", sa.Text()),
        sa.Column("tags", postgresql.ARRAY(sa.String())),
        sa.Column("is_blocked", sa.Boolean(), server_default=sa.false()),
        sa.Column("consent_at", sa.DateTime(timezone=True)),
    )
    op.create_unique_constraint("uq_client_telegram_id", "client", ["telegram_id"])
    op.create_index("ix_client_telegram_id", "client", ["telegram_id"])
    op.create_index("ix_client_phone", "client", ["phone"])

    op.create_table(
        "service",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("master_id", sa.BigInteger(), sa.ForeignKey("master.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("duration_min", sa.Integer(), nullable=False),
        sa.Column("buffer_min", sa.Integer(), server_default="0"),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("deposit_amount", sa.Numeric(10, 2)),
        sa.Column("category", sa.String(80)),
        sa.Column("photo_url", sa.String(512)),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
    )
    op.create_index("ix_service_master_id", "service", ["master_id"])

    op.create_table(
        "appointment",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("master_id", sa.BigInteger(), sa.ForeignKey("master.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", sa.BigInteger(), sa.ForeignKey("client.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", appointment_status, server_default="pending", nullable=False),
        sa.Column("source", appointment_source, server_default="site", nullable=False),
        sa.Column("comment", sa.Text()),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_appointment_master_id", "appointment", ["master_id"])
    op.create_index("ix_appointment_master_start", "appointment", ["master_id", "start_at"])

    # Ядро защиты от двойного бронирования: нет пересечений активных записей мастера.
    op.execute(
        """
        ALTER TABLE appointment
        ADD CONSTRAINT appointment_no_overlap
        EXCLUDE USING gist (
            master_id WITH =,
            tstzrange(start_at, end_at) WITH &&
        )
        WHERE (status NOT IN ('cancelled', 'no_show'))
        """
    )

    op.create_table(
        "appointment_services",
        sa.Column("appointment_id", sa.BigInteger(), sa.ForeignKey("appointment.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("service_id", sa.BigInteger(), sa.ForeignKey("service.id", ondelete="RESTRICT"), primary_key=True),
    )

    op.create_table(
        "working_hours",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("master_id", sa.BigInteger(), sa.ForeignKey("master.id", ondelete="CASCADE"), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time()),
        sa.Column("end_time", sa.Time()),
        sa.Column("is_day_off", sa.Boolean(), server_default=sa.false()),
    )
    op.create_index("ix_working_hours_master_id", "working_hours", ["master_id"])

    op.create_table(
        "time_off",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("master_id", sa.BigInteger(), sa.ForeignKey("master.id", ondelete="CASCADE"), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reason", sa.String(255)),
    )
    op.create_index("ix_time_off_master_id", "time_off", ["master_id"])

    op.create_table(
        "reminder",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("appointment_id", sa.BigInteger(), sa.ForeignKey("appointment.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", reminder_type, nullable=False),
        sa.Column("send_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("status", reminder_status, server_default="scheduled", nullable=False),
    )
    op.create_index("ix_reminder_appointment_id", "reminder", ["appointment_id"])
    op.create_index("ix_reminder_status_send_at", "reminder", ["status", "send_at"])

    op.create_table(
        "review",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("client_id", sa.BigInteger(), sa.ForeignKey("client.id", ondelete="CASCADE"), nullable=False),
        sa.Column("appointment_id", sa.BigInteger(), sa.ForeignKey("appointment.id", ondelete="SET NULL")),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text()),
        sa.Column("status", review_status, server_default="pending", nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_table("review")
    op.drop_index("ix_reminder_status_send_at", table_name="reminder")
    op.drop_index("ix_reminder_appointment_id", table_name="reminder")
    op.drop_table("reminder")
    op.drop_index("ix_time_off_master_id", table_name="time_off")
    op.drop_table("time_off")
    op.drop_index("ix_working_hours_master_id", table_name="working_hours")
    op.drop_table("working_hours")
    op.drop_table("appointment_services")
    op.execute("ALTER TABLE appointment DROP CONSTRAINT IF EXISTS appointment_no_overlap")
    op.drop_index("ix_appointment_master_start", table_name="appointment")
    op.drop_index("ix_appointment_master_id", table_name="appointment")
    op.drop_table("appointment")
    op.drop_index("ix_service_master_id", table_name="service")
    op.drop_table("service")
    op.drop_index("ix_client_phone", table_name="client")
    op.drop_index("ix_client_telegram_id", table_name="client")
    op.drop_table("client")
    op.drop_table("master")

    bind = op.get_bind()
    for enum in (
        review_status, reminder_status, reminder_type,
        appointment_source, appointment_status,
    ):
        enum.drop(bind, checkfirst=True)
