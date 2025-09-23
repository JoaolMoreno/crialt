"""initial_migration

Revision ID: 2c600628c868
Revises: 
Create Date: 2025-09-13 20:13:31.424729

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '2c600628c868'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Criação das tabelas SEM constraints de chave estrangeira
    op.create_table('users',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('admin', 'architect', 'assistant', name='userrole'), nullable=False),
        sa.Column('avatar', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('clients',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('document', sa.String(), nullable=False),
        sa.Column('document_type', sa.Enum('cpf', 'cnpj', name='documenttype'), nullable=False),
        sa.Column('rg_ie', sa.String(), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('secondary_email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('mobile', sa.String(), nullable=True),
        sa.Column('whatsapp', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=True),
        sa.Column('first_access', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('address', sa.JSON(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stage_types',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scope', sa.JSON(), nullable=True),
        sa.Column('default_duration_days', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('projects',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('total_value', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default=sa.text("'BRL'")),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('estimated_end_date', sa.Date(), nullable=False),
        sa.Column('actual_end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'active', 'paused', 'completed', 'cancelled', name='projectstatus'), nullable=False, server_default=sa.text("'draft'")),
        sa.Column('work_address', sa.JSON(), nullable=True),
        sa.Column('scope', sa.JSON(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by_id', UUID(as_uuid=True), nullable=False),
        sa.Column('current_stage_id', UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stages',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'cancelled', 'on_hold', name='stagestatus'), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('planned_start_date', sa.Date(), nullable=False),
        sa.Column('actual_start_date', sa.Date(), nullable=True),
        sa.Column('planned_end_date', sa.Date(), nullable=False),
        sa.Column('actual_end_date', sa.Date(), nullable=True),
        sa.Column('value', sa.Numeric(10, 2), nullable=False),
        sa.Column('specific_data', sa.JSON(), nullable=True),
        sa.Column('progress_percentage', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('project_id', UUID(as_uuid=True), nullable=False),
        sa.Column('stage_type_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_by_id', UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_to_id', UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('files',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('original_name', sa.String(), nullable=False),
        sa.Column('stored_name', sa.String(), nullable=False, unique=True),
        sa.Column('path', sa.String(), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('category', sa.Enum('document', 'image', 'video', 'plan', 'render', 'contract', name='filecategory'), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('project_id', UUID(as_uuid=True), nullable=True),
        sa.Column('client_id', UUID(as_uuid=True), nullable=True),
        sa.Column('stage_id', UUID(as_uuid=True), nullable=True),
        sa.Column('uploaded_by_id', UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stored_name')
    )
    op.create_table('project_clients',
        sa.Column('project_id', UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint('project_id', 'client_id')
    )
    op.create_table('tasks',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('todo', 'in_progress', 'completed', 'cancelled', name='taskstatus'), nullable=False, server_default=sa.text("'todo'")),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='taskpriority'), nullable=False, server_default=sa.text("'medium'")),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('stage_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_by_id', UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_to_id', UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('chunked_uploads',
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('upload_id', sa.String(length=255), nullable=False),
                    sa.Column('filename', sa.String(length=255), nullable=False),
                    sa.Column('total_chunks', sa.Integer(), nullable=False),
                    sa.Column('chunk_size', sa.Integer(), nullable=False),
                    sa.Column('total_size', sa.Integer(), nullable=False),
                    sa.Column('file_checksum', sa.String(length=64), nullable=True),
                    sa.Column('mime_type', sa.String(length=255), nullable=True),
                    sa.Column('category', sa.String(length=50), nullable=True),
                    sa.Column('project_id', sa.UUID(), nullable=True),
                    sa.Column('client_id', sa.UUID(), nullable=True),
                    sa.Column('stage_id', sa.UUID(), nullable=True),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('uploaded_by_id', sa.UUID(), nullable=False),
                    sa.Column('uploaded_chunks', sa.Text(), nullable=True),
                    sa.Column('is_completed', sa.Boolean(), nullable=True),
                    sa.Column('final_file_id', sa.UUID(), nullable=True),
                    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    # 2. Adição das constraints de chave estrangeira e índices
    op.create_foreign_key('fk_stages_assigned_to_id_users', 'stages', 'users', ['assigned_to_id'], ['id'])
    op.create_foreign_key('fk_stages_created_by_id_users', 'stages', 'users', ['created_by_id'], ['id'])
    op.create_foreign_key('fk_stages_project_id_projects', 'stages', 'projects', ['project_id'], ['id'])
    op.create_foreign_key('fk_stages_stage_type_id_stage_types', 'stages', 'stage_types', ['stage_type_id'], ['id'])
    op.create_foreign_key('fk_files_client_id_clients', 'files', 'clients', ['client_id'], ['id'])
    op.create_foreign_key('fk_files_project_id_projects', 'files', 'projects', ['project_id'], ['id'])
    op.create_foreign_key('fk_files_stage_id_stages', 'files', 'stages', ['stage_id'], ['id'])
    op.create_foreign_key('fk_files_uploaded_by_id_users', 'files', 'users', ['uploaded_by_id'], ['id'])
    op.create_foreign_key('fk_project_clients_client_id_clients', 'project_clients', 'clients', ['client_id'], ['id'])
    op.create_foreign_key('fk_project_clients_project_id_projects', 'project_clients', 'projects', ['project_id'], ['id'])
    op.create_foreign_key('fk_tasks_assigned_to_id_users', 'tasks', 'users', ['assigned_to_id'], ['id'])
    op.create_foreign_key('fk_tasks_created_by_id_users', 'tasks', 'users', ['created_by_id'], ['id'])
    op.create_foreign_key('fk_tasks_stage_id_stages', 'tasks', 'stages', ['stage_id'], ['id'])
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_clients_created_at'), 'clients', ['created_at'], unique=False)
    op.create_index(op.f('ix_clients_document'), 'clients', ['document'], unique=True)
    op.create_index(op.f('ix_clients_email'), 'clients', ['email'], unique=True)
    op.create_index(op.f('ix_clients_name'), 'clients', ['name'], unique=False)
    op.create_index(op.f('ix_projects_created_at'), 'projects', ['created_at'], unique=False)
    op.create_index(op.f('ix_projects_current_stage_id'), 'projects', ['current_stage_id'], unique=False)
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)
    op.create_index(op.f('ix_projects_start_date'), 'projects', ['start_date'], unique=False)
    op.create_index(op.f('ix_projects_status'), 'projects', ['status'], unique=False)
    op.create_index(op.f('ix_stages_name'), 'stages', ['name'], unique=False)
    op.create_index(op.f('ix_stages_stage_type_id'), 'stages', ['stage_type_id'], unique=False)
    op.create_index(op.f('ix_stage_types_name'), 'stage_types', ['name'], unique=False)
    op.create_index(op.f('ix_chunked_uploads_upload_id'), 'chunked_uploads', ['upload_id'], unique=True)
    # ### end Alembic commands ###

    # Inserir dados padrão para tipos de etapa
    from sqlalchemy import text
    import json

    # Dados padrão dos tipos de etapa baseados no fluxo da Crialt Arquitetura
    stage_types_data = [
        {
            'name': 'Levantamento',
            'description': 'Levantamento do local e medições',
            'scope': {
                'local_visita': {'type': 'string', 'required': True, 'label': 'Local da Visita'},
                'data_visita': {'type': 'date', 'required': True, 'label': 'Data da Visita'},
                'responsavel': {'type': 'string', 'required': True, 'label': 'Responsável'},
                'observacoes_local': {'type': 'text', 'required': False, 'label': 'Observações do Local'}
            },
            'default_duration_days': 3
        },
        {
            'name': 'Briefing',
            'description': 'Reunião para definição do briefing com o cliente',
            'scope': {
                'preferencias_cliente': {'type': 'text', 'required': True, 'label': 'Preferências do Cliente'},
                'orcamento_cliente': {'type': 'number', 'required': False, 'label': 'Orçamento do Cliente'},
                'prazo_desejado': {'type': 'date', 'required': False, 'label': 'Prazo Desejado'},
                'estilo_preferido': {'type': 'string', 'required': False, 'label': 'Estilo Preferido'}
            },
            'default_duration_days': 2
        },
        {
            'name': 'Estudo Preliminar',
            'description': 'Desenvolvimento do estudo preliminar',
            'scope': {
                'numero_alternativas': {'type': 'number', 'required': True, 'label': 'Número de Alternativas'},
                'tipo_apresentacao': {'type': 'string', 'required': True, 'label': 'Tipo de Apresentação'},
                'revisoes_incluidas': {'type': 'number', 'required': True, 'label': 'Revisões Incluídas'},
                'entrega_3d': {'type': 'boolean', 'required': False, 'label': 'Entrega de Imagens 3D'}
            },
            'default_duration_days': 14
        },
        {
            'name': 'Projeto Executivo',
            'description': 'Desenvolvimento do projeto executivo detalhado',
            'scope': {
                'plantas_incluidas': {'type': 'array', 'required': True, 'label': 'Plantas Incluídas'},
                'especialidades': {'type': 'array', 'required': True, 'label': 'Especialidades (Elétrica, Hidráulica, etc.)'},
                'detalhamentos': {'type': 'array', 'required': False, 'label': 'Detalhamentos Específicos'},
                'memorial_descritivo': {'type': 'boolean', 'required': True, 'label': 'Memorial Descritivo'}
            },
            'default_duration_days': 30
        },
        {
            'name': 'Assessoria Pós-Projeto',
            'description': 'Acompanhamento e assessoria durante a execução',
            'scope': {
                'cronograma_visitas': {'type': 'array', 'required': True, 'label': 'Cronograma de Visitas'},
                'tipo_acompanhamento': {'type': 'string', 'required': True, 'label': 'Tipo de Acompanhamento'},
                'responsabilidades': {'type': 'text', 'required': True, 'label': 'Responsabilidades'},
                'prazo_assessoria': {'type': 'number', 'required': True, 'label': 'Prazo da Assessoria (meses)'}
            },
            'default_duration_days': 90
        }
    ]

    # Inserir os tipos de etapa padrão
    connection = op.get_bind()
    import time
    from datetime import datetime

    base_timestamp = time.time()

    for i, stage_type in enumerate(stage_types_data):
        scope_json = json.dumps(stage_type['scope'])
        # Adiciona 1 segundo para cada stage_type para garantir ordem diferente
        stage_created_at = datetime.fromtimestamp(base_timestamp + i)

        connection.execute(
            text("""
                INSERT INTO stage_types (id, name, description, scope, default_duration_days, is_active, created_at, updated_at)
                VALUES (
                    gen_random_uuid(),
                    :name,
                    :description,
                    :scope,
                    :default_duration_days,
                    true,
                    :created_at,
                    :updated_at
                )
            """),
            {
                'name': stage_type['name'],
                'description': stage_type['description'],
                'scope': scope_json,
                'default_duration_days': stage_type['default_duration_days'],
                'created_at': stage_created_at,
                'updated_at': stage_created_at
            }
        )


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tasks')
    op.drop_table('project_clients')
    op.drop_table('files')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_stages_name'), table_name='stages')
    op.drop_table('stages')
    op.drop_table('stage_types')
    op.drop_index(op.f('ix_projects_status'), table_name='projects')
    op.drop_index(op.f('ix_projects_start_date'), table_name='projects')
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_index(op.f('ix_projects_current_stage_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_created_at'), table_name='projects')
    op.drop_table('projects')
    op.drop_index(op.f('ix_clients_name'), table_name='clients')
    op.drop_index(op.f('ix_clients_email'), table_name='clients')
    op.drop_index(op.f('ix_clients_document'), table_name='clients')
    op.drop_index(op.f('ix_clients_created_at'), table_name='clients')
    op.drop_table('clients')
    op.drop_table('chunked_uploads')
    # ### end Alembic commands ###
