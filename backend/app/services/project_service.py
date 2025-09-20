from datetime import datetime, UTC
import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from ..models import Project, Client, Stage
from ..models.stage_type import StageType
from ..models.project import project_clients
from ..schemas.project import ProjectCreate, ProjectUpdate, PaginatedProjects, ProjectRead
from ..schemas.stage import StageStatus
from ..utils.cache import cache


class ProjectService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.logger = logging.getLogger(__name__)

    def create_project(self, project_data: ProjectCreate, user_id: str) -> Project:
        self._validate_project_data(project_data)

        for client_id in project_data.clients:
            client = self.db.get(Client, client_id)
            if not client:
                raise HTTPException(status_code=400, detail="Cliente não foi encontrado.")

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

        try:
            self.db.add(project)
            self.db.flush()

            for client_id in project_data.clients:
                self.db.execute(project_clients.insert().values(project_id=project.id, client_id=client_id))

            if project_data.stages:
                self._create_custom_stages(project, project_data.stages, user_id)
            else:
                self._create_default_stages(project, user_id)

            self.db.commit()
            self.db.refresh(project)
            # Invalida cache de listagem e dashboard após criar
            cache.invalidate('get_projects')
            cache.invalidate('dashboard')
            return project

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Não foi possível criar o projeto.")

    def _create_default_stages(self, project: Project, user_id: str) -> None:
        stage_types = self.db.query(StageType).filter(StageType.is_active == True).order_by(StageType.created_at).all()

        created_stages = []
        for idx, stage_type in enumerate(stage_types, start=1):
            stage = Stage(
                name=str(stage_type.name),
                description=str(stage_type.description) if stage_type.description else None,
                order=idx,
                status=StageStatus.pending,
                planned_start_date=project.start_date,
                planned_end_date=project.estimated_end_date,
                value=0,
                project_id=project.id,
                stage_type_id=stage_type.id,
                created_by_id=user_id,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            self.db.add(stage)
            self.db.flush()
            created_stages.append(stage)

        self._set_initial_current_stage(project, created_stages)

    def _create_custom_stages(self, project: Project, stages_data: list, user_id: str) -> None:
        created_stages = []
        for stage_data in stages_data:
            stage_type = self.db.get(StageType, stage_data.stage_type_id)
            if not stage_type:
                raise HTTPException(status_code=400, detail="Tipo de etapa não foi encontrado.")

            stage = Stage(
                name=stage_data.name or str(stage_type.name),
                description=stage_data.description or (str(stage_type.description) if stage_type.description else None),
                order=stage_data.order,
                status=StageStatus.pending,
                planned_start_date=stage_data.planned_start_date or project.start_date,
                planned_end_date=stage_data.planned_end_date or project.estimated_end_date,
                value=stage_data.value or 0,
                progress_percentage=stage_data.progress_percentage or 0,
                notes=stage_data.notes,
                project_id=project.id,
                stage_type_id=stage_data.stage_type_id,
                created_by_id=user_id,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
            self.db.add(stage)
            self.db.flush()
            created_stages.append(stage)

        self._set_initial_current_stage(project, created_stages)

    def _set_initial_current_stage(self, project: Project, stages: list) -> None:
        if not stages:
            project.current_stage_id = None
            return

        sorted_stages = sorted(stages, key=lambda s: s.order)
        current_stage = None

        for stage in sorted_stages:
            if stage.status == StageStatus.in_progress:
                current_stage = stage
                break

        if not current_stage:
            for stage in sorted_stages:
                if stage.status == StageStatus.pending:
                    current_stage = stage
                    break

        if not current_stage:
            current_stage = sorted_stages[0]

        project.current_stage_id = current_stage.id

    def calculate_progress(self, project_id: str) -> float:
        project = self.db.get(Project, project_id)
        if not project or not project.stages:
            return 0.0
        total = len(project.stages)
        concluido = sum(1 for s in project.stages if s.status == StageStatus.completed)
        return round((concluido / total) * 100, 2) if total else 0.0

    def get_project(self, project_id, actor=None, client_resource_permission=None):
        self.logger.info(f"[DB] get_project: project_id={project_id}, actor={actor}, client_resource_permission={client_resource_permission}")
        project = self.db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        if client_resource_permission and actor:
            client_ids = [str(client.id) for client in project.clients]
            client_resource_permission(client_ids, actor)
        return ProjectRead.model_validate(project, from_attributes=True)

    def get_project_progress(self, project_id, actor=None, client_resource_permission=None):
        project = self.db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        if client_resource_permission and actor:
            client_ids = [str(client.id) for client in project.clients]
            client_resource_permission(client_ids, actor)
        if not project.stages:
            return {"progress": 0.0}
        total = len(project.stages)
        concluido = sum(1 for s in project.stages if s.status == StageStatus.completed)
        return {"progress": round((concluido / total) * 100, 2) if total else 0.0}

    def get_projects(self, limit, offset, order_by, order_dir, name, status, start_date, client_id, stage_name, stage_type, stage, search):
        cache_params = {
            'limit': limit,
            'offset': offset,
            'order_by': order_by,
            'order_dir': order_dir,
            'name': name,
            'status': status,
            'start_date': str(start_date) if start_date else None,
            'client_id': client_id,
            'stage_name': stage_name,
            'stage_type': stage_type,
            'stage': stage,
            'search': search
        }
        cached_result = cache.get('get_projects', cache_params)
        if cached_result:
            self.logger.info(f"[CACHE] get_projects: {cache_params}")
            return cached_result
        self.logger.info(f"[DB] get_projects: {cache_params}")
        query = self.db.query(Project)
        if name:
            query = query.filter(Project.name.ilike(f"%{name}%"))
        if status:
            query = query.filter(Project.status == status)
        if start_date:
            query = query.filter(Project.start_date >= start_date)
        if client_id:
            query = query.join(Project.clients).filter(Client.id == client_id)
        if stage_name:
            query = query.join(Project.stages).filter(Stage.name.ilike(f"%{stage_name}%"))
        if stage_type:
            query = query.join(Project.stages).filter(Stage.stage_type_id == stage_type)
        if stage:
            query = query.join(Project.stages).filter(Stage.id == stage)
        if search:
            query = query.filter(Project.name.ilike(f"%{search}%"))
        if hasattr(Project, order_by):
            order_col = getattr(Project, order_by)
            if order_dir == "desc":
                order_col = order_col.desc()
            else:
                order_col = order_col.asc()
            query = query.order_by(order_col)
        total = query.count()
        items = query.offset(offset).limit(limit).all()
        result = PaginatedProjects(
            total=total,
            count=len(items),
            offset=offset,
            limit=limit,
            items=[ProjectRead.model_validate(p, from_attributes=True) for p in items]
        )
        cache.set('get_projects', cache_params, result)
        return result

    def get_my_projects(self, actor, limit, offset, order_by, order_dir, name, status, start_date, client_id, search):
        self.logger.info(f"[DB] get_my_projects: actor={actor}, limit={limit}, offset={offset}, order_by={order_by}, order_dir={order_dir}, name={name}, status={status}, start_date={start_date}, client_id={client_id}, search={search}")
        query = self.db.query(Project)
        if hasattr(actor, "id"):
            query = query.join(Project.clients).filter(Client.id == actor.id)
        if name:
            query = query.filter(Project.name.ilike(f"%{name}%"))
        if status:
            query = query.filter(Project.status == status)
        if start_date:
            query = query.filter(Project.start_date >= start_date)
        if client_id:
            query = query.join(Project.clients).filter(Client.id == client_id)
        if search:
            query = query.filter(Project.name.ilike(f"%{search}%"))
        if hasattr(Project, order_by):
            order_col = getattr(Project, order_by)
            if order_dir == "desc":
                order_col = order_col.desc()
            else:
                order_col = order_col.asc()
            query = query.order_by(order_col)
        total = query.count()
        items = query.offset(offset).limit(limit).all()
        return PaginatedProjects(
            total=total,
            count=len(items),
            offset=offset,
            limit=limit,
            items=[ProjectRead.model_validate(p, from_attributes=True) for p in items]
        )

    def update_project(self, project_id: str, project_data: ProjectUpdate) -> Project:
        project = self.db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não foi encontrado")

        if not project_data.stages or len(project_data.stages) == 0:
            raise ValueError("O projeto deve conter pelo menos uma etapa (stage).")

        try:
            updated_fields = project_data.model_dump(exclude_unset=True, exclude={"stages", "clients"})

            if "start_date" in updated_fields or "estimated_end_date" in updated_fields:
                start_date = updated_fields.get("start_date", project.start_date)
                end_date = updated_fields.get("estimated_end_date", project.estimated_end_date)
                if end_date <= start_date:
                    raise HTTPException(status_code=400, detail="Data de término deve ser posterior à data de início.")

            for field, value in updated_fields.items():
                setattr(project, field, value)

            project.updated_at = datetime.now(UTC)

            if project_data.clients is not None:
                self._update_project_clients(project, project_data.clients)

            if project_data.stages is not None:
                self._update_project_stages(project, project_data.stages)

            self.db.commit()
            self.db.refresh(project)

            cache.invalidate('get_projects')
            cache.invalidate('dashboard')
            return project

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Não foi possível atualizar o projeto.")

    def _update_project_clients(self, project: Project, new_client_ids: list) -> None:
        for client_id in new_client_ids:
            client = self.db.get(Client, client_id)
            if not client:
                raise HTTPException(status_code=400, detail="Cliente não foi encontrado.")

        self.db.execute(project_clients.delete().where(project_clients.c.project_id == project.id))

        for client_id in new_client_ids:
            self.db.execute(project_clients.insert().values(project_id=project.id, client_id=client_id))

    def _update_project_stages(self, project: Project, stages_data: list) -> None:
        stage_ids_to_keep = []
        current_stage_still_exists = False

        for stage_data in stages_data:
            if stage_data.id:
                stage = self.db.get(Stage, stage_data.id)
                if stage and stage.project_id == project.id:
                    self._update_existing_stage(stage, stage_data)
                    stage_ids_to_keep.append(stage.id)

                    if project.current_stage_id == stage.id:
                        current_stage_still_exists = True
                else:
                    raise HTTPException(status_code=400, detail="Etapa não foi encontrada ou não pertence ao projeto.")
            else:
                new_stage = self._create_new_stage(project, stage_data)
                stage_ids_to_keep.append(new_stage.id)

        for stage in list(project.stages):
            if stage.id not in stage_ids_to_keep:
                if project.current_stage_id == stage.id:
                    current_stage_still_exists = False
                self.db.delete(stage)

        self._update_current_stage_logic(project, stage_ids_to_keep, current_stage_still_exists)

    def _update_current_stage_logic(self, project: Project, stage_ids_to_keep: list, current_stage_still_exists: bool) -> None:
        if current_stage_still_exists and project.current_stage_id in stage_ids_to_keep:
            return

        remaining_stages = self.db.query(Stage).filter(
            Stage.project_id == project.id,
            Stage.id.in_(stage_ids_to_keep)
        ).order_by(Stage.order.asc()).all()

        if not remaining_stages:
            project.current_stage_id = None
            return

        current_stage = None

        for stage in remaining_stages:
            if stage.status == StageStatus.in_progress:
                current_stage = stage
                break

        if not current_stage:
            for stage in remaining_stages:
                if stage.status == StageStatus.pending:
                    current_stage = stage
                    break

        if not current_stage:
            current_stage = remaining_stages[0]

        project.current_stage_id = current_stage.id if current_stage else None

    def _update_existing_stage(self, stage: Stage, stage_data) -> None:
        updated_fields = stage_data.model_dump(exclude_unset=True, exclude={"id"})

        if "stage_type_id" in updated_fields:
            stage_type = self.db.get(StageType, updated_fields["stage_type_id"])
            if not stage_type:
                raise HTTPException(status_code=400, detail="Tipo de etapa não foi encontrado.")

        for field, value in updated_fields.items():
            setattr(stage, field, value)

        stage.updated_at = datetime.now(UTC)

    def _create_new_stage(self, project: Project, stage_data) -> Stage:
        stage_type = self.db.get(StageType, stage_data.stage_type_id)
        if not stage_type:
            raise HTTPException(status_code=400, detail="Tipo de etapa não foi encontrado.")

        stage = Stage(
            name=stage_data.name or str(stage_type.name),
            description=stage_data.description or (str(stage_type.description) if stage_type.description else None),
            order=stage_data.order,
            status=getattr(stage_data, "status", StageStatus.pending),
            planned_start_date=stage_data.planned_start_date,
            actual_start_date=getattr(stage_data, "actual_start_date", None),
            planned_end_date=stage_data.planned_end_date,
            actual_end_date=getattr(stage_data, "actual_end_date", None),
            value=stage_data.value or 0,
            progress_percentage=stage_data.progress_percentage or 0,
            notes=stage_data.notes,
            assigned_to_id=getattr(stage_data, "assigned_to_id", None),
            project_id=project.id,
            stage_type_id=stage_data.stage_type_id,
            created_by_id=project.created_by_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )

        self.db.add(stage)
        self.db.flush()
        return stage

    def update_current_stage(self, project_id: str, stage_id: str) -> Project:
        project = self.db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não foi encontrado")

        stage = self.db.get(Stage, stage_id)
        if not stage or stage.project_id != project.id:
            raise HTTPException(status_code=400, detail="Etapa não foi encontrada ou não pertence ao projeto")

        try:
            project.current_stage_id = stage_id
            project.updated_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(project)
            return project
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=f"Erro ao atualizar etapa atual: {str(e)}")

    def delete_project(self, project_id: str) -> bool:
        project = self.db.get(Project, project_id)
        if not project:
            return False

        try:
            self.db.delete(project)
            self.db.commit()
            cache.invalidate('get_projects')
            cache.invalidate('dashboard')
            return True
        except IntegrityError:
            self.db.rollback()
            return False

    def _validate_project_data(self, project_data) -> None:
        if project_data.estimated_end_date <= project_data.start_date:
            raise HTTPException(status_code=400, detail="Data de término deve ser posterior à data de início.")

        if not project_data.name or not project_data.name.strip():
            raise HTTPException(status_code=400, detail="Nome do projeto é obrigatório.")

        if project_data.total_value < 0:
            raise HTTPException(status_code=400, detail="Valor total do projeto não pode ser negativo.")

        if not project_data.clients:
            raise HTTPException(status_code=400, detail="Pelo menos um cliente deve ser vinculado ao projeto.")

    def get_projects_by_client(self, client_id, actor, limit, offset, order_by, order_dir, name, status, start_date, search, client_resource_permission=None):
        self.logger.info(f"[DB] get_projects_by_client: client_id={client_id}, actor={actor}, limit={limit}, offset={offset}, order_by={order_by}, order_dir={order_dir}, name={name}, status={status}, start_date={start_date}, search={search}")
        query = self.db.query(Project)
        query = query.join(Project.clients).filter(Client.id == client_id)
        if name:
            query = query.filter(Project.name.ilike(f"%{name}%"))
        if status:
            query = query.filter(Project.status == status)
        if start_date:
            query = query.filter(Project.start_date >= start_date)
        if search:
            query = query.filter(Project.name.ilike(f"%{search}%"))
        if hasattr(Project, order_by):
            order_col = getattr(Project, order_by)
            if order_dir == "desc":
                order_col = order_col.desc()
            else:
                order_col = order_col.asc()
            query = query.order_by(order_col)
        total = query.count()
        items = query.offset(offset).limit(limit).all()
        if client_resource_permission and actor:
            client_resource_permission([client_id], actor)
        return PaginatedProjects(
            total=total,
            count=len(items),
            offset=offset,
            limit=limit,
            items=[ProjectRead.model_validate(p, from_attributes=True) for p in items]
        )
