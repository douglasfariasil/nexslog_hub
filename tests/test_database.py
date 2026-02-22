from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from nexslog.database import database


def test_create_db_and_tables_monkeypatched(monkeypatch):
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr(database, 'engine', engine)
    database.create_db_and_tables()
    assert 'order' in SQLModel.metadata.tables or any(
        'order' in t for t in SQLModel.metadata.tables
    )


def test_get_session_generator_returns_session():
    gen = database.get_session()
    session = next(gen)
    assert hasattr(session, 'exec')
    # close generator to clean up
    try:
        gen.close()
    except RuntimeError:
        pass
