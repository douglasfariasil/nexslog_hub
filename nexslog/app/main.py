from fastapi import FastAPI

from nexslog.app.models import ERPOrderInput

# O Endpoint da API
app = FastAPI(title='Centro de Interoperabilidade Logística')


@app.get('/')
def read_root():
    return {'message': 'Central on-line', 'version': '1.0.0'}


@app.post('/ingerir/erp')
async def receive_erp_order(order: ERPOrderInput):
    # Aqui entrará a lógica para salvar no Banco de Dados
    # e notificar o WMS futuramente.
    print(f'Recebido pedido {order.order_id} do ERP')

    return {
        'status': 'success',
        'message': 'Pedido processado e normalizado',
        'internal_id': f'HUB-{order.order_id}',
    }
