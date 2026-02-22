from http import HTTPStatus

import pytest
from fastapi import HTTPException
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from nexslog.app.adapters.wms import WMSAdapter
from nexslog.database.models import Order

engine = create_engine(
    'sqlite:///:memory:',
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)
SQLModel.metadata.create_all(engine)


def test_process_status_update_success():
    with Session(engine) as session:
        o = Order(order_id='X1', customer_name='C', total_value=10.0)
        session.add(o)
        session.commit()
        session.refresh(o)

        updated = WMSAdapter.process_status_update(session, 'X1', 'PICKING')
        assert updated.status == 'PICKING'


def test_process_status_update_not_found():
    with Session(engine) as session:
        with pytest.raises(HTTPException) as exc:
            WMSAdapter.process_status_update(session, 'NOEX', 'PICKING')
        assert exc.value.status_code == HTTPStatus.NOT_FOUND


def test_process_status_update_block_if_shipped():
    with Session(engine) as session:
        o = Order(
            order_id='S1', customer_name='C2', total_value=1.0, status='SHIPPED'
        )
        session.add(o)
        session.commit()
        session.refresh(o)

        with pytest.raises(HTTPException) as exc:
            WMSAdapter.process_status_update(session, 'S1', 'PICKING')
        assert exc.value.status_code == HTTPStatus.BAD_REQUEST


def test_process_status_update_no_change_returns_object():
    with Session(engine) as session:
        o = Order(
            order_id='NC1', customer_name='C3', total_value=5.0, status='PENDING'
        )
        session.add(o)
        session.commit()
        session.refresh(o)

        returned = WMSAdapter.process_status_update(session, 'NC1', 'PENDING')
        assert returned is not None
        assert returned.status == 'PENDING'
