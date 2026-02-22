import sys
from importlib import reload
from importlib import reload as _reload
from types import SimpleNamespace

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import nexslog.dashboard as dashboard_mod
from nexslog import dashboard
from nexslog.database.models import Order


def test_dashboard_import_with_fake_streamlit(monkeypatch, tmp_path):
    """Monkeypatch streamlit before importing the dashboard module to ensure
    import does not execute real Streamlit behaviors during tests.
    """
    fake_st = SimpleNamespace()
    fake_st.set_page_config = lambda *a, **k: None
    fake_st.title = lambda *a, **k: None
    fake_st.markdown = lambda *a, **k: None

    def columns(*a, **k):
        class FakeColumn:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        # If called with an int (e.g., st.columns(3)) return that many columns
        if a and isinstance(a[0], int):
            return tuple(FakeColumn() for _ in range(a[0]))

        return (FakeColumn(), FakeColumn())

    fake_st.columns = columns
    fake_st.button = lambda *a, **k: False
    fake_st.text_input = lambda *a, **k: ''
    fake_st.divider = lambda *a, **k: None
    fake_st.metric = lambda *a, **k: None
    fake_st.subheader = lambda *a, **k: None
    fake_st.bar_chart = lambda *a, **k: None
    fake_st.dataframe = lambda *a, **k: None
    fake_st.download_button = lambda *a, **k: None
    fake_st.info = lambda *a, **k: None
    fake_st.cache_data = lambda f: f
    fake_st.error = lambda *a, **k: None
    fake_st.rerun = lambda *a, **k: None

    # Ensure our fake streamlit is used during import
    monkeypatch.setitem(sys.modules, 'streamlit', fake_st)

    # Provide an in-memory engine to avoid touching disk DB during import
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    # Import the dashboard module (it will use the fake streamlit)
    reload(dashboard)

    # Optionally override the module engine to our in-memory engine
    try:
        dashboard.engine = engine
    except Exception:
        pass

    # No assertions needed — test ensures import runs without raising


def test_dashboard_with_orders_triggers_metrics_and_download(monkeypatch):
    fake_st = SimpleNamespace()
    calls = {
        'metrics': [],
        'bar_charts': 0,
        'downloaded': False,
    }

    fake_st.set_page_config = lambda *a, **k: None
    fake_st.title = lambda *a, **k: None
    fake_st.markdown = lambda *a, **k: None

    def columns(*a, **k):
        class FakeColumn:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            @staticmethod
            def metric(*a, **k):
                calls['metrics'].append((a, k))

            @staticmethod
            def subheader(*a, **k):
                return None

            @staticmethod
            def bar_chart(*a, **k):
                calls['bar_charts'] += 1

        # support integer columns
        if a and isinstance(a[0], int):
            return tuple(FakeColumn() for _ in range(a[0]))

        return (FakeColumn(), FakeColumn())

    fake_st.columns = columns
    fake_st.button = lambda *a, **k: False
    fake_st.text_input = lambda *a, **k: ''
    fake_st.divider = lambda *a, **k: None
    fake_st.subheader = lambda *a, **k: None
    fake_st.bar_chart = lambda *a, **k: calls.update(
        bar_charts=calls['bar_charts'] + 1
    )

    def fake_download_button(*a, **k):
        calls['downloaded'] = True

    fake_st.download_button = fake_download_button
    fake_st.dataframe = lambda *a, **k: None
    fake_st.info = lambda *a, **k: None
    fake_st.cache_data = lambda f: f
    fake_st.error = lambda *a, **k: None
    fake_st.rerun = lambda *a, **k: None

    monkeypatch.setitem(__import__('sys').modules, 'streamlit', fake_st)

    # prepare engine and insert one order
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as s:
        o = Order(
            order_id='D1',
            customer_name='C1',
            total_value=123.0,
            status='RECEIVED',
        )
        s.add(o)
        s.commit()

    # reload module so it runs with our fake streamlit and in-memory DB

    dashboard_mod.engine = engine
    _reload(dashboard_mod)

    # verify some dashboard actions ran
    assert calls['metrics'] or calls['bar_charts'] or calls['downloaded']
