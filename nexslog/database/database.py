from sqlmodel import Session, SQLModel, create_engine

# A URL vem do ambiente que definimos no docker compose
sqlite_url = 'sqlite:///./banco.db'


# O engine é o "motor" que conversa com o Postgres
engine = create_engine(
    sqlite_url, connect_args={'check_same_thread': False}, echo=True
)


def create_db_and_tables():
    """Cria as tabelas no arquivo banco.db"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Gera as tabelas no banco de dados para cada requisição"""
    with Session(engine) as session:
        yield session
