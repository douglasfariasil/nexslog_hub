import os
from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select

from nexslog.app.adapters.wms import WMSAdapter
from nexslog.app.database import create_db_and_tables, get_session
from nexslog.app.models import Order

# O Endpoint da API
app = FastAPI(title='NexsLog Hub')


# Cria as tabelas assim que o app inicia
@app.on_event('startup')
def on_startup():
    if os.getenv('TESTING') != 'True':
        create_db_and_tables()


@app.post('/ingerir/erp')
async def receive_erp_order(
    order_data: Order, session: Session = Depends(get_session)
):

    # Adiciona o pedido ao banco de dados
    session.add(order_data)
    session.commit()
    session.refresh(order_data)

    return {
        'status': 'success',
        'hub_id': order_data.order_id,
        'message': f'Pedido {order_data.order_id} registrado no NexsLog',
    }


@app.patch('/ingerir/wms/atualizar')
async def update_from_wms(
    order_id: str, new_status: str, session: Session = Depends(get_session)
):
    # O Adapter já valida se existe e se pode atualizar
    updated_order = WMSAdapter.process_status_update(
        session, order_id, new_status
    )

    return {
        'status': 'updated',
        'order_id': updated_order.order_id,
        'new_status': updated_order.status,
    }


@app.patch('/ingerir/tms/dispatch')
async def dispatch_order(
    order_id: str, tracking: str, session: Session = Depends(get_session)
):
    statement = select(Order).where(Order.order_id == order_id)
    db_order = session.exec(statement).first()

    if not db_order:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Pedido não encontrado'
        )

    db_order.status = 'SHIPPED'
    db_order.tracking_code = tracking
    session.add(db_order)
    session.commit()
    return {'message': 'Pedido enviado', 'tracking': tracking}


# Para subir a máquina container: docker compose up --build
# Para abrir o navegador: http://localhost:8080/docs
