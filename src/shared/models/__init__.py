"""SQLAlchemy models for every table in design.md §6.

Importing this package registers every table on ``Base.metadata``, which Alembic reads.
"""

from shared.models.base import Base
from shared.models.company import Company

__all__ = ["Base", "Company"]
