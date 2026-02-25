# Usa uma imagem leve do Python
FROM python:3.13-slim

# Define o diretório de trabalho
WORKDIR /app

# 1. Instala dependências do sistema primeiro
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Instala o Poetry
RUN pip install --no-cache-dir poetry

# 3. Copia apenas os arquivos de configuração do Poetry
COPY pyproject.toml poetry.lock* ./

# 4. Configura Poetry e instala dependências
# (sem criar venv dentro do container)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# 5. Copia o restante do código
COPY . .

# Expõe as portas
EXPOSE 8000
EXPOSE 8501
