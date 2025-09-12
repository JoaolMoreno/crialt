import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool, create_engine

# Adiciona o diretório backend ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__)) + "/.."))
from backend.app.models import base

# Carrega variáveis do .env se existir
load_dotenv()

# Configuração do Alembic
config = context.config

# Configura o log
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Pega a URL do banco de dados diretamente do ambiente
database_url = os.environ.get('DATABASE_URL')

# Define o target_metadata para autogeração
target_metadata = base.Base.metadata

def run_migrations_offline():
    context.configure(
        url=database_url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(database_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
