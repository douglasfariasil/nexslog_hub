import os
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from nexslog.app.main import app, get_session

os.environ['TESTING'] = 'True'


engine_test = create_engine(
    'sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool
)


# --- CONFIGURAÇÃO DO BANCO DE TESTES (SQLlite em memória) ---
@pytest.fixture(name='session')
def session_fixture():

    SQLModel.metadata.create_all(engine_test)
    with Session(engine_test) as session:
        yield session
    SQLModel.metadata.drop_all(engine_test)


@pytest.fixture(name='client')
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_create_order_from_erp(client: TestClient):
    """Testa se o ERP consegue registrar um pedido"""

    response = client.post(
        '/ingerir/erp',
        json={
            'order_id': 'PED-TESTE-01',
            'customer_name': 'Douglas',
            'total_value': 150.50,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['status'] == 'success'


def test_update_status_from_wms(client: TestClient):
    """Testa a interoperabilidade: WMS atualizando pedido do ERP"""

    client.post(
        '/ingerir/erp',
        json={
            'order_id': 'PED-WMS-01',
            'customer_name': 'Logistica S.A',
            'total_value': 1000.0,
        },
    )

    response = client.patch(
        '/ingerir/wms/atualizar',
        params={'order_id': 'PED-WMS-01', 'new_status': 'PICKING'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['new_status'] == 'PICKING'


def test_update_non_existent_order(client: TestClient):
    """Testa se o sistema nega uma atualização de pedido que
    não existe"""

    response = client.patch(
        '/ingerir/wms/atualizar',
        params={'order_id': 'NAO-EXISTE', 'new_status': 'PICKING'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'não encontrado' in response.json()['detail']


def test_prevent_update_shipped_order(client: TestClient):
    """Testa se o sistema impede mudar o status de um pedido já enviado"""

    # Cria o pedido
    client.post(
        '/ingerir/erp',
        json={
            'order_id': 'PED-FINALIZADO',
            'customer_name': 'Cliente Teste',
            'total_value': 50.0,
        },
    )

    # Despacha o pedido
    client.patch(
        '/ingerir/tms/dispatch',
        params={'order_id': 'PED-FINALIZADO', 'tracking': 'ABC123XYZ'},
    )

    # Tenta forçar um novo status via WMS

    response = client.patch(
        '/ingerir/wms/atualizar',
        params={'order_id': 'PED-FINALIZADO', 'new_status': 'PICKING'},
    )

    # Valida se bloqueou com 400(Bad Request)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'já enviado' in response.json()['detail']


def test_full_supply_chain_flow(client: TestClient):
    """
    Simula o ciclo de vida completo:
    ERP (Cria) -> WMS (Processa) -> TMS (Envia) -> Bloqueio WMS
    """

    order_id = 'PED-FLOW-123'

    # --- PASSO 1: ERP Ingerindo Pedido ---

    erp_res = client.post(
        '/ingerir/erp',
        json={
            'order_id': order_id,
            'customer_name': 'Rex Logistica',
            'total_value': 2500.0,
        },
    )
    assert erp_res.status_code == HTTPStatus.OK

    # --- PASSO 2: WMS Atualizando para PICKING ---

    wms_res = client.patch(
        '/ingerir/wms/atualizar',
        params={'order_id': order_id, 'new_status': 'PICKING'},
    )
    assert wms_res.status_code == HTTPStatus.OK
    assert wms_res.json()['new_status'] == 'PICKING'

    # --- PASSO 3: TMS Despachando o Pedido ---

    tms_res = client.patch(
        '/ingerir/tms/dispatch',
        params={'order_id': order_id, 'tracking': 'BR-123456-X'},
    )
    assert tms_res.status_code == HTTPStatus.OK
    assert tms_res.json()['message'] == 'Pedido enviado'

    # --- PASSO 4: Validação de Segurança (WMS tentando voltar status) ---

    block_res = client.patch(
        '/ingerir/wms/atualizar',
        params={'order_id': order_id, 'new_status': 'PICKING'},
    )
    assert block_res.status_code == HTTPStatus.BAD_REQUEST
    assert 'já enviado' in block_res.json()['detail']

    print(f'\n✅ Fluxo completo validado para o pedido: {order_id}')
