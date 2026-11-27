"""companies

Revision ID: 0001
Revises:
Create Date: 2026-11-25 09:15:46.913129

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=False),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "slug",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "ats",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "board_token",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "enabled",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "last_fetch_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "ats IN ('greenhouse', 'lever', 'ashby')",
            name=op.f("ck_companies_ats"),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_companies"),
        ),
        sa.UniqueConstraint(
            "ats",
            "board_token",
            name=op.f("uq_companies_ats_board_token"),
        ),
        sa.UniqueConstraint(
            "slug",
            name=op.f("uq_companies_slug"),
        ),
    )


def downgrade() -> None:
    op.drop_table("companies")
