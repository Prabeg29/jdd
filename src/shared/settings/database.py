"""``settings.database``: the Postgres connection (design.md §7)."""

from typing import Literal

from pydantic import Field, SecretStr, model_validator
from sqlalchemy import URL

from shared.schemas.base import StrictModel


class DatabaseSettings(StrictModel):
    """
    - ``host``: Neon's pooled host for Lambdas, the direct host for Alembic.
    - ``password``: held as a secret so it never appears in reprs or logs.
    - ``pooled``: True for the PgBouncer (pooled) endpoint, which turns off client-side
      prepared statements so transaction pooling stays safe.
    - ``sslmode``: TLS is required by default; local docker Postgres uses ``disable``.
    - ``connect_*``: retry with exponential backoff to absorb Neon waking from
      scale-to-zero.
    """

    host: str
    port: int = 5432
    name: str
    user: str
    password: SecretStr
    pooled: bool = True
    sslmode: Literal["disable", "allow", "prefer", "require", "verify-ca", "verify-full"] = (
        "require"
    )
    connect_attempts: int = Field(default=5, ge=1)
    connect_backoff_base_s: float = Field(default=0.5, gt=0)
    connect_backoff_max_s: float = Field(default=8.0, gt=0)

    @model_validator(mode="after")
    def _backoff_bounds(self) -> "DatabaseSettings":
        if self.connect_backoff_max_s < self.connect_backoff_base_s:
            raise ValueError("connect_backoff_max_s must be >= connect_backoff_base_s")
        return self

    @property
    def url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.name,
            query={"sslmode": self.sslmode},
        )
