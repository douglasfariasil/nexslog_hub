
from fastapi import Depends, FastAPI
from sqlmodel import Session

from nexslog.app.database import create_db_and_tables, get_session
from nexslog.app.models import Order

# O Endpoint da API
app = FastAPI(title='NexsLog Hub')


# Cria as tabelas assim que o app inicia
@app.on_event('startup')
def on_startup():
    create_db_and_tables()


@app.post('/ingerir/erp')
async def receive_erp_order(
    order_data: Order,
    session: Session = Depends(get_session)
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

# Para subir a máquina container docker compose up --build
# Para abrir o navegador http://localhost:8080/docs
