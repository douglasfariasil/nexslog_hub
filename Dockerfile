FROM python:3.13-slim


# Impede que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 


WORKDIR /app


# Instala o Poetry
RUN pip install poetry


# Instala dependências
COPY pyproject.toml poetry.lock* ./


# Configura o Poetry para não criar um ambiente virtual dentro do container 
# (o próprio container já é um ambiente isolado)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root


# Copia o código da aplicação
COPY . .


# Comando para rodar a API
CMD ["uvicorn", "nexslog.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
