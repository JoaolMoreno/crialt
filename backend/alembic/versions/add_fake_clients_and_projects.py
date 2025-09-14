"""
Migration para inserir clientes e projetos fake para testes
"""
import uuid
from datetime import datetime, timedelta, UTC
from alembic import op
from sqlalchemy import text
from faker import Faker
import json
import re

revision = 'add_fake_clients_and_projects'
down_revision = 'add_admin_user'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    now = datetime.now(UTC)
    fake = Faker('pt_BR')

    # Buscar o id do admin
    admin_result = conn.execute(text("SELECT id FROM users WHERE username = 'admin' LIMIT 1"))
    admin_row = admin_result.fetchone()
    if not admin_row:
        raise Exception("Usuário admin não encontrado. Execute a migration de admin antes.")
    admin_id = str(admin_row[0])

    # Buscar todos os tipos de etapa disponíveis ORDENADOS POR created_at
    stage_types_result = conn.execute(text("SELECT id, name FROM stage_types WHERE is_active = true ORDER BY created_at"))
    stage_types = [{"id": str(row[0]), "name": row[1]} for row in stage_types_result.fetchall()]

    if not stage_types:
        raise Exception("Nenhum tipo de etapa encontrado. Execute a migration inicial antes.")

    fake_clients = []
    for i in range(50):
        email = fake.unique.email()
        document_raw = fake.unique.cpf()
        document = re.sub(r'\D', '', document_raw)
        address = {
            "street": fake.street_name(),
            "number": fake.building_number(),
            "neighborhood": fake.bairro(),
            "city": fake.city(),
            "state": fake.estado_sigla(),
            "zip": fake.postcode(),
            "complement": fake.word()
        }
        client = {
            "id": str(uuid.uuid4()),
            "name": fake.name(),
            "document": document,
            "document_type": "cpf",
            "rg_ie": fake.rg(),
            "birth_date": fake.date_of_birth(minimum_age=18, maximum_age=70),
            "email": email,
            "secondary_email": fake.email(),
            "phone": fake.phone_number(),
            "mobile": fake.cellphone_number(),
            "whatsapp": fake.cellphone_number(),
            "address": json.dumps(address),
            "notes": fake.sentence(),
            "is_active": True,
            "password_hash": None,
            "first_access": True,
            "created_at": now,
            "updated_at": now
        }
        fake_clients.append(client)
        conn.execute(
            text("""
            INSERT INTO clients (
                id, name, document, document_type, rg_ie, birth_date, email, secondary_email, phone, mobile, whatsapp, address, notes, is_active, password_hash, first_access, created_at, updated_at
            ) VALUES (
                :id, :name, :document, :document_type, :rg_ie, :birth_date, :email, :secondary_email, :phone, :mobile, :whatsapp, :address, :notes, :is_active, :password_hash, :first_access, :created_at, :updated_at
            )
            """), client
        )

    status_list = ["active", "draft", "paused", "completed", "cancelled"]
    stage_status_list = ["pending", "in_progress", "completed", "cancelled", "on_hold"]
    payment_status_list = ["pending", "partial", "paid"]

    for client in fake_clients:
        work_address = {
            "street": fake.street_name(),
            "number": fake.building_number(),
            "neighborhood": fake.bairro(),
            "city": fake.city(),
            "state": fake.estado_sigla(),
            "zip": fake.postcode(),
            "complement": fake.word()
        }
        scope = {
            "summary": fake.sentence(),
            "details": fake.text(max_nb_chars=200)
        }
        status = fake.random_element(status_list)
        start_date = now.date() - timedelta(days=fake.random_int(0, 90))
        estimated_end_date = start_date + timedelta(days=fake.random_int(30, 180))
        # Aleatoriza a data final: se for menor que hoje, salva; se for maior, deixa None
        actual_end_date = estimated_end_date if estimated_end_date < now.date() else None
        project = {
            "id": str(uuid.uuid4()),
            "name": fake.bs().capitalize(),
            "description": fake.text(max_nb_chars=100),
            "total_value": round(fake.pyfloat(left_digits=5, right_digits=2, positive=True), 2),
            "currency": "BRL",
            "start_date": start_date,
            "estimated_end_date": estimated_end_date,
            "actual_end_date": actual_end_date,
            "status": status,
            "work_address": json.dumps(work_address),
            "scope": json.dumps(scope),
            "notes": fake.sentence(),
            "created_at": now,
            "updated_at": now,
            "created_by_id": admin_id
        }
        conn.execute(
            text("""
            INSERT INTO projects (
                id, name, description, total_value, currency, start_date, estimated_end_date, actual_end_date, status, work_address, scope, notes, created_at, updated_at, created_by_id
            ) VALUES (
                :id, :name, :description, :total_value, :currency, :start_date, :estimated_end_date, :actual_end_date, :status, :work_address, :scope, :notes, :created_at, :updated_at, :created_by_id
            )
            """), project
        )

        # Vincular cliente ao projeto
        conn.execute(
            text("""
            INSERT INTO project_clients (project_id, client_id) VALUES (:project_id, :client_id)
            """), {"project_id": project["id"], "client_id": client["id"]}
        )

        # Criar etapas para o projeto baseadas nos tipos de etapa disponíveis
        total_project_value = project["total_value"]
        stage_ids = []
        for idx, stage_type in enumerate(stage_types, start=1):
            # Distribuir o valor do projeto entre as etapas
            stage_value = round(total_project_value / len(stage_types), 2)
            if idx == len(stage_types):  # Última etapa pega o valor restante
                stage_value = total_project_value - (stage_value * (len(stage_types) - 1))

            # Calcular datas das etapas
            days_per_stage = (estimated_end_date - start_date).days // len(stage_types)
            stage_start = start_date + timedelta(days=(idx - 1) * days_per_stage)
            stage_end = start_date + timedelta(days=idx * days_per_stage)

            # Status da etapa baseado no status do projeto e ordem
            if status == "completed":
                stage_status = "completed"
            elif status == "active" and idx <= 2:
                stage_status = fake.random_element(["completed", "in_progress"])
            elif status == "active":
                stage_status = fake.random_element(["pending", "in_progress"])
            else:
                stage_status = "pending"

            # Status de pagamento
            if stage_status == "completed":
                payment_status = fake.random_element(["paid", "partial"])
            else:
                payment_status = "pending"

            # Progresso baseado no status
            if stage_status == "completed":
                progress = 100
            elif stage_status == "in_progress":
                progress = fake.random_int(10, 90)
            else:
                progress = 0

            # Dados específicos da etapa (exemplo baseado no tipo)
            specific_data = {}
            if stage_type["name"] == "Levantamento":
                specific_data = {
                    "local_visita": work_address["street"] + ", " + work_address["number"],
                    "data_visita": str(stage_start),
                    "responsavel": fake.name(),
                    "observacoes_local": fake.sentence()
                }
            elif stage_type["name"] == "Briefing":
                specific_data = {
                    "preferencias_cliente": fake.text(max_nb_chars=100),
                    "orcamento_cliente": float(total_project_value),
                    "estilo_preferido": fake.random_element(["Moderno", "Clássico", "Minimalista", "Industrial"])
                }

            stage = {
                "id": str(uuid.uuid4()),
                "name": stage_type["name"],
                "description": f"Etapa de {stage_type['name']} do projeto {project['name']}",
                "order": idx,
                "status": stage_status,
                "planned_start_date": stage_start,
                "actual_start_date": stage_start if stage_status in ["in_progress", "completed"] else None,
                "planned_end_date": stage_end,
                "actual_end_date": stage_end if stage_status == "completed" else None,
                "value": stage_value,
                "payment_status": payment_status,
                "specific_data": json.dumps(specific_data) if specific_data else None,
                "progress_percentage": progress,
                "notes": fake.sentence(),
                "created_at": now,
                "updated_at": now,
                "project_id": project["id"],
                "stage_type_id": stage_type["id"],
                "created_by_id": admin_id,
                "assigned_to_id": admin_id
            }

            conn.execute(
                text("""
                INSERT INTO stages (
                    id, name, description, "order", status, planned_start_date, actual_start_date,
                    planned_end_date, actual_end_date, value, payment_status, specific_data,
                    progress_percentage, notes, created_at, updated_at, project_id, stage_type_id,
                    created_by_id, assigned_to_id
                ) VALUES (
                    :id, :name, :description, :order, :status, :planned_start_date, :actual_start_date,
                    :planned_end_date, :actual_end_date, :value, :payment_status, :specific_data,
                    :progress_percentage, :notes, :created_at, :updated_at, :project_id, :stage_type_id,
                    :created_by_id, :assigned_to_id
                )
                """), stage
            )
            stage_ids.append(stage["id"])

        if stage_ids:
            conn.execute(
                text("""
                UPDATE projects SET current_stage_id = :stage_id WHERE id = :project_id
                """), {"stage_id": stage_ids[0], "project_id": project["id"]}
            )

def downgrade():
    # Deletar etapas dos projetos fake
    op.execute("DELETE FROM stages WHERE project_id IN (SELECT id FROM projects WHERE created_by_id = (SELECT id FROM users WHERE username = 'admin'))")
    # Deletar relacionamentos projeto-cliente
    op.execute("DELETE FROM project_clients WHERE client_id IN (SELECT id FROM clients WHERE email LIKE '%@example.%')")
    # Deletar projetos fake
    op.execute("DELETE FROM projects WHERE created_by_id = (SELECT id FROM users WHERE username = 'admin')")
    # Deletar clientes fake
    op.execute("DELETE FROM clients WHERE email LIKE '%@example.%'")
