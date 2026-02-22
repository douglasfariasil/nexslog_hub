from http import HTTPStatus


def test_criar_pedido_erp_sucesso(client):
    """Testa se a API aceita um pedido novo do ERP corretamente"""

    payload = {
        'order_id': 'TEST-123',
        'customer_name': 'Cliente Teste',
        'total_value': 100.0,
    }

    response = client.post('/ingerir/erp', json=payload)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['status'] == 'success'
    assert data['hub_id'] == 'TEST-123'
    assert 'registrado no NexsLog' in data['message']


def test_atualizar_wms_sucesso(client):
    """Testa a atualização de status pelo WMS"""

    # Primeiro criamos, depois atualizamos
    client.post(
        '/ingerir/erp',
        json={
            'order_id': 'TEST-WMS',
            'customer_name': 'T',
            'total_value': 10,
        },
    )

    response = client.patch(
        '/ingerir/wms/atualizar',
        params={'order_id': 'TEST-WMS', 'new_status': 'PICKING'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['status'] == 'updated'
    assert data['new_status'] == 'PICKING'
    assert data['order_id'] == 'TEST-WMS'
