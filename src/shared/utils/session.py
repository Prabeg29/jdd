from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from shared.settings.base import settings

database = settings.database

# NullPool: Lambda containers are short-lived, so Neon's pooled (PgBouncer) endpoint does
# the pooling. On that endpoint, client-side prepared statements must be off.
engine = create_engine(
    database.url,
    poolclass=NullPool,
    connect_args={"prepare_threshold": None} if database.pooled else {},
)

# expire_on_commit=False keeps loaded attributes readable after a commit
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
