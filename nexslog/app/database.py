import os

from sqlmodel import Session, SQLModel, create_engine

# A URL vem do ambiente que definimos no docker compose
DATABASE_URL = os.getenv(
    'DATABASE_URL', 'postgresql://user:pass@db:5432/interop_db'
)


# sqlite_name = 'banco.db'
# DATABASE_URL = f'sqlite:///{sqlite_name}'


# O engine é o "motor" que conversa com o Postgres
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Cria as tabelas no banco de dados se elas não existirem"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Gera as tabelas no banco de dados para cada requisição"""
    with Session(engine) as session:
        yield session
