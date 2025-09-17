from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from ..models.task import Task
from ..schemas.task import TaskRead, TaskCreate, TaskUpdate, PaginatedTasks
from ..models.stage import Stage
from ..utils.cache import cache

class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def get_tasks(self, limit: int, offset: int, order_by: str, order_dir: str, title: Optional[str], status: Optional[str], priority: Optional[str], due_date: Optional[str], stage_id: Optional[str], created_by_id: Optional[str], assigned_to_id: Optional[str]) -> PaginatedTasks:
        cache_params = {
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "order_dir": order_dir,
            "title": title,
            "status": status,
            "priority": priority,
            "due_date": due_date,
            "stage_id": stage_id,
            "created_by_id": created_by_id,
            "assigned_to_id": assigned_to_id
        }
        cached = cache.get("tasks", cache_params)
        if cached:
            self.logger.info(f"[CACHE] get_tasks: params={cache_params}")
            return cached
        self.logger.info(f"[DB] get_tasks: params={cache_params}")
        query = self.db.query(Task)
        if title:
            query = query.filter(Task.title.ilike(f"%{title}%"))
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if due_date:
            query = query.filter(Task.due_date == due_date)
        if stage_id:
            query = query.filter(Task.stage_id == stage_id)
        if created_by_id:
            query = query.filter(Task.created_by_id == created_by_id)
        if assigned_to_id:
            query = query.filter(Task.assigned_to_id == assigned_to_id)
        if hasattr(Task, order_by):
            order_col = getattr(Task, order_by)
            if order_dir == "desc":
                order_col = order_col.desc()
            else:
                order_col = order_col.asc()
            query = query.order_by(order_col)
        total = query.count()
        items = query.offset(offset).limit(limit).all()
        result = PaginatedTasks(
            total=total,
            count=len(items),
            offset=offset,
            limit=limit,
            items=[TaskRead.model_validate(t, from_attributes=True) for t in items]
        )
        cache.set("tasks", cache_params, result)
        return result

    def get_tasks_by_stage(self, stage_id: str, actor, client_resource_permission) -> List[TaskRead]:
        stage = self.db.get(Stage, stage_id)
        if not stage:
            raise HTTPException(status_code=404, detail="Etapa não encontrada")
        client_ids = [str(client.id) for client in stage.project.clients]
        client_resource_permission(client_ids, actor)
        tasks = self.db.query(Task).filter(Task.stage_id == stage_id).all()
        return [TaskRead.model_validate(t, from_attributes=True) for t in tasks]

    def get_tasks_by_project(self, project_id: str, actor, client_resource_permission) -> List[TaskRead]:
        from ..models.project import Project
        project = self.db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
        client_ids = [str(client.id) for client in project.clients]
        client_resource_permission(client_ids, actor)
        tasks = self.db.query(Task).join(Stage).filter(Stage.project_id == project_id).all()
        return [TaskRead.model_validate(t, from_attributes=True) for t in tasks]

    def get_task(self, task_id: str, actor, client_resource_permission) -> TaskRead:
        task = self.db.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        client_ids = [str(client.id) for client in task.stage.project.clients]
        client_resource_permission(client_ids, actor)
        return TaskRead.model_validate(task, from_attributes=True)

    def create_task(self, task_data: TaskCreate) -> TaskRead:
        task = Task(**task_data.model_dump())
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        cache.invalidate("tasks")
        cache.invalidate("dashboard")
        return TaskRead.model_validate(task, from_attributes=True)

    def update_task(self, task_id: str, task_data: TaskUpdate) -> TaskRead:
        task = self.db.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        task.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(task)
        cache.invalidate("tasks")
        cache.invalidate("dashboard")
        return TaskRead.model_validate(task, from_attributes=True)

    def delete_task(self, task_id: str) -> dict:
        task = self.db.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        self.db.delete(task)
        self.db.commit()
        cache.invalidate("tasks")
        cache.invalidate("dashboard")
        return {"message": "Tarefa removida com sucesso"}
