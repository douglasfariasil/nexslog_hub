import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

# Indica ao app que está em modo de teste para impedir criação automática
# do banco de dados de produção durante os testes.
os.environ['TESTING'] = 'True'

from nexslog.app.main import app, get_session

# Engine exclusiva para testes (em memória)
test_engine = create_engine(
    'sqlite:///:memory:',
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)


@pytest.fixture(name='session')
def session_fixture():
    # Cria as tabelas na memória antes de cada teste
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    # Remove tudo após o teste
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name='client')
def client_fixture(session: Session):
    # Sobrescreve a dependência get_session da API para usar a nossa de teste
    def get_session_override():
        return session

    # Injeta a sessão de teste na aplicação
    app.dependency_overrides[get_session] = get_session_override

    # Criando o cliente de teste
    with TestClient(app) as c:
        yield c
    # Limpa as sobrescritas após o teste
    app.dependency_overrides.clear()
