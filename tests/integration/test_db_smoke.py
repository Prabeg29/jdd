from sqlalchemy import Engine, text


def test_select_one(db_engine: Engine) -> None:
    with db_engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar_one() == 1


def test_session_database_is_fresh(db_engine: Engine) -> None:
    with db_engine.connect() as conn:
        name = conn.execute(text("SELECT current_database()")).scalar_one()
        tables = conn.execute(
            text("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
        ).scalar_one()
    assert name.startswith("job_discovery_test_")
    assert tables == 0
