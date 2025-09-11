"""
Migration para inserir usuário admin
"""
import uuid
from datetime import datetime, UTC
from alembic import op
import os
import sys
from sqlalchemy import text

# Revisão e dependências
revision = 'add_admin_user'
down_revision = '92b25a1995e4'
branch_labels = None
depends_on = None
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.security import get_password_hash

def upgrade():
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if not admin_email or not admin_password:
        raise Exception("ADMIN_EMAIL e ADMIN_PASSWORD devem estar definidos nas variáveis de ambiente.")

    conn = op.get_bind()
    result = conn.execute(
        text("SELECT id FROM users WHERE email = :email OR username = :username"),
        {"email": admin_email, "username": "admin"}
    )
    if result.fetchone():
        # Usuário já existe, não faz nada
        return

    admin_id = str(uuid.uuid4())
    now = datetime.now(UTC)
    password_hash = get_password_hash(admin_password)
    conn.execute(
        text("""
        INSERT INTO users (
            id, name, email, username, password_hash, role, is_active, created_at, updated_at
        ) VALUES (:id, :name, :email, :username, :password_hash, :role, :is_active, :created_at, :updated_at)
        """),
        {
            "id": admin_id,
            "name": "Administrador",
            "email": admin_email,
            "username": "admin",
            "password_hash": password_hash,
            "role": "admin",
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
    )

def downgrade():
    op.execute("DELETE FROM users WHERE username = 'admin'")
