"""Declarative base shared by every table (design.md §6).

Every column is declared in full with ``mapped_column``: SQL type, nullability, keys and
defaults are written out rather than inferred from the ``Mapped[...]`` annotation.
"""

from sqlalchemy import BigInteger, CheckConstraint, Identity, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Deterministic constraint names, so Alembic migrations can refer to them.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class IdMixin:
    """Surrogate ``bigint`` identity primary key, placed first in every table."""

    id: Mapped[int] = mapped_column(
        "id",
        BigInteger,
        Identity(always=False),
        primary_key=True,
        nullable=False,
        sort_order=-1,
    )


def one_of(column: str, values: tuple[str, ...]) -> CheckConstraint:
    """CHECK that ``column`` holds one of ``values``.

    Text plus a CHECK instead of a Postgres enum type: adding a value is a one-line
    migration with no ``ALTER TYPE``.
    """
    allowed = ", ".join(f"'{v}'" for v in values)
    return CheckConstraint(f"{column} IN ({allowed})", name=column)
