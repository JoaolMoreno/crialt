import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Adiciona o diretório backend ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

# Carrega variáveis do .env se existir
load_dotenv()

# Configuração do Alembic
config = context.config

# Configura o log
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define a URL do banco de dados a partir da variável de ambiente
config.set_main_option('sqlalchemy.url', os.environ.get('DATABASE_URL'))

from app.models import base  # importa o Base

# Define o target_metadata para autogeração
target_metadata = base.Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
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
