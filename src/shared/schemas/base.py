"""Shared base for Pydantic models of files and stored documents."""

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Rejects unknown keys and is immutable once parsed."""

    model_config = ConfigDict(extra="forbid", frozen=True)
