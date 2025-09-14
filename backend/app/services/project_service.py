from datetime import datetime, UTC

from sqlalchemy.orm import Session

from ..models import Project, Client, Stage
from ..models.stage_type import StageType
from ..models.project import project_clients
from ..schemas.project import ProjectCreate
from ..schemas.stage import StageStatus


class ProjectService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_project(self, project_data: ProjectCreate, user_id: str) -> Project:
        # Validação de datas
        if project_data.estimated_end_date <= project_data.start_date:
            raise ValueError("Data de término deve ser posterior à data de início.")
        # Criação do projeto
        project = Project(
            name=project_data.name,
            description=project_data.description,
            total_value=project_data.total_value,
            currency=project_data.currency,
            start_date=project_data.start_date,
            estimated_end_date=project_data.estimated_end_date,
            status=project_data.status,
            work_address=project_data.work_address,
            scope=project_data.scope,
            notes=project_data.notes,
            created_by_id=user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        self.db.add(project)
        self.db.flush()
        # Vincular clientes
        for client_id in project_data.clients:
            client = self.db.get(Client, client_id)
            if client:
                self.db.execute(project_clients.insert().values(project_id=project.id, client_id=client.id))

        # Criação automática de etapas padrão baseadas nos tipos cadastrados
        stage_types = self.db.query(StageType).filter(StageType.is_active == True).order_by(StageType.name).all()

        created_stages = []
        for idx, stage_type in enumerate(stage_types, start=1):
            etapa = Stage(
                name=stage_type.name,
                description=stage_type.description,
                order=idx,
                status=StageStatus.pending,
                planned_start_date=project.start_date,
                planned_end_date=project.estimated_end_date,
                value=0,
                payment_status="pending",
                project_id=project.id,
                stage_type_id=stage_type.id,
                created_by_id=user_id,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            self.db.add(etapa)
            self.db.flush()
            created_stages.append(etapa)

        etapa_ativa = next((e for e in created_stages if e.status in [StageStatus.in_progress, StageStatus.pending]), None)
        if not etapa_ativa and created_stages:
            etapa_ativa = created_stages[0]
        if etapa_ativa:
            project.current_stage_id = etapa_ativa.id
        self.db.commit()
        return project

    def calculate_progress(self, project_id: str) -> float:
        # Cálculo automático de progresso
        project = self.db.get(Project, project_id)
        if not project or not project.stages:
            return 0.0
        total = len(project.stages)
        concluido = sum(1 for s in project.stages if s.status == StageStatus.completed)
        return round((concluido / total) * 100, 2) if total else 0.0

    def validate_dates(self, start: datetime, end: datetime) -> bool:
        return end > start

    def get_project(self, project_id: str) -> Project:
        project = self.db.get(Project, project_id)
        if not project:
            raise ValueError("Projeto não encontrado")
        return project

    def update_project(self, project_id: str, project_data) -> Project:
        project = self.db.get(Project, project_id)
        if not project:
            return None

        for field, value in project_data.model_dump(exclude_unset=True).items():
            if field != "stages":
                setattr(project, field, value)
        project.updated_at = datetime.now()

        if hasattr(project_data, "stages") and project_data.stages is not None:
            stage_ids = []
            for stage_data in project_data.stages:
                stage_id = getattr(stage_data, "id", None)
                if stage_id:
                    stage = self.db.get(Stage, stage_id)
                    if stage and stage.project_id == project.id:
                        for field, value in stage_data.model_dump(exclude_unset=True).items():
                            setattr(stage, field, value)
                        stage.updated_at = datetime.now()
                        stage_ids.append(stage.id)
                else:

                    new_stage = Stage(
                        project_id=project.id,
                        **stage_data.model_dump(exclude_unset=True)
                    )
                    self.db.add(new_stage)
                    self.db.flush()
                    stage_ids.append(new_stage.id)

            for stage in list(project.stages):
                if stage.id not in stage_ids:
                    self.db.delete(stage)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_project(self, project_id: str) -> bool:
        project = self.db.get(Project, project_id)
        if not project:
            return False
        self.db.delete(project)
        self.db.commit()
