"""Shared pytest fixtures.

Integration tests run against the local Postgres from docker-compose.yml. A fresh,
uniquely named database is created once per test session and dropped at the end.
Override the server with TEST_DATABASE_ADMIN_URL (must point at a maintenance DB
the test user can CREATE DATABASE from).
"""

import os
import uuid
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

DEFAULT_ADMIN_URL = "postgresql+psycopg://postgres:postgres@127.0.0.1:5433/postgres"


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    """Create a fresh database for this session and yield its SQLAlchemy URL."""
    admin_url = make_url(os.environ.get("TEST_DATABASE_ADMIN_URL", DEFAULT_ADMIN_URL))
    db_name = f"job_discovery_test_{uuid.uuid4().hex[:12]}"

    admin = create_engine(admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    try:
        with admin.connect() as conn:
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    except Exception as exc:  # pragma: no cover - environment problem
        admin.dispose()
        pytest.fail(
            f"Cannot create test database on {admin_url.render_as_string(hide_password=True)}: "
            f"{exc}\nIs Postgres running? Try `docker compose up -d --wait`.",
            pytrace=False,
        )

    try:
        yield admin_url.set(database=db_name).render_as_string(hide_password=False)
    finally:
        with admin.connect() as conn:
            conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}" WITH (FORCE)'))
        admin.dispose()


@pytest.fixture(scope="session")
def db_engine(database_url: str) -> Iterator[Engine]:
    engine = create_engine(database_url, poolclass=NullPool)
    try:
        yield engine
    finally:
        engine.dispose()
