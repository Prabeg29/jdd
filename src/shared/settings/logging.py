"""``settings.log``: logging settings (``LOG__LEVEL``)."""

from typing import Literal

from shared.schemas.base import StrictModel


class LogSettings(StrictModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
