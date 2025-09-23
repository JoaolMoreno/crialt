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
down_revision = '2c600628c868'
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
    """
    Remove admin user. This will only work if no data is referenced by the admin user.
    In production, you might want to reassign ownership before deletion.
    """
    conn = op.get_bind()

    # Check if admin user exists
    result = conn.execute(
        text("SELECT id FROM users WHERE username = 'admin'")
    )
    admin_user = result.fetchone()

    if not admin_user:
        # Admin user doesn't exist, nothing to do
        return

    admin_id = admin_user[0]

    # Check if admin user is referenced by other tables
    # Check stages
    stages_count = conn.execute(
        text("SELECT COUNT(*) FROM stages WHERE created_by_id = :admin_id OR assigned_to_id = :admin_id"),
        {"admin_id": admin_id}
    ).fetchone()[0]

    # Check tasks
    tasks_count = conn.execute(
        text("SELECT COUNT(*) FROM tasks WHERE created_by_id = :admin_id OR assigned_to_id = :admin_id"),
        {"admin_id": admin_id}
    ).fetchone()[0]

    # Check projects
    projects_count = conn.execute(
        text("SELECT COUNT(*) FROM projects WHERE created_by_id = :admin_id"),
        {"admin_id": admin_id}
    ).fetchone()[0]

    # Check files
    files_count = conn.execute(
        text("SELECT COUNT(*) FROM files WHERE uploaded_by_id = :admin_id"),
        {"admin_id": admin_id}
    ).fetchone()[0]

    if stages_count > 0 or tasks_count > 0 or projects_count > 0 or files_count > 0:
        print(f"Warning: Cannot delete admin user as it is referenced by:")
        if stages_count > 0:
            print(f"  - {stages_count} stage(s)")
        if tasks_count > 0:
            print(f"  - {tasks_count} task(s)")
        if projects_count > 0:
            print(f"  - {projects_count} project(s)")
        if files_count > 0:
            print(f"  - {files_count} file(s)")
        print("Skipping admin user deletion to maintain data integrity.")
        return

    # If no references exist, safe to delete
    conn.execute(
        text("DELETE FROM users WHERE username = 'admin'")
    )
