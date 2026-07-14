"""admin_user (CRM auth)

Revision ID: 0002_admin
Revises: 0001_init
Create Date: 2026-07-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_admin"
down_revision: str | None = "0001_init"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "admin_user",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("totp_secret", sa.String(64)),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
    )
    op.create_unique_constraint("uq_admin_user_email", "admin_user", ["email"])
    op.create_index("ix_admin_user_email", "admin_user", ["email"])


def downgrade() -> None:
    op.drop_index("ix_admin_user_email", table_name="admin_user")
    op.drop_table("admin_user")
