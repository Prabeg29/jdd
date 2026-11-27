from datetime import datetime

from sqlalchemy import Boolean, DateTime, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from shared.models.base import Base, IdMixin, one_of

ATS_VALUES = ("greenhouse", "lever", "ashby")


class Company(IdMixin, Base):
    """A company and its one board, synced from ``companies.yaml``."""

    __tablename__ = "companies"
    __table_args__ = (
        UniqueConstraint("ats", "board_token"),
        one_of("ats", ATS_VALUES),
    )

    name: Mapped[str] = mapped_column(
        "name",
        Text,
        nullable=False,
    )
    # Normalized name: the company's identity across edits of companies.yaml.
    slug: Mapped[str] = mapped_column(
        "slug",
        Text,
        nullable=False,
        unique=True,
    )
    ats: Mapped[str] = mapped_column(
        "ats",
        Text,
        nullable=False,
    )
    board_token: Mapped[str] = mapped_column(
        "board_token",
        Text,
        nullable=False,
    )
    enabled: Mapped[bool] = mapped_column(
        "enabled",
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    # Latest successful fetch. Empty until the first one and after an ATS switch.
    last_fetch_at: Mapped[datetime | None] = mapped_column(
        "last_fetch_at",
        DateTime(timezone=True),
        nullable=True,
    )
