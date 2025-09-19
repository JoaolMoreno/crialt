from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
import logging

from ..models import StageType
from ..models.user import User
from ..schemas.stage_type import StageTypeRead, StageTypeCreate, StageTypeUpdate, PaginatedStageTypes
from ..utils.cache import cache


class StageTypeService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def get_stage_types(self, actor: Any, limit: int, offset: int, order_by: str, order_dir: str, name: Optional[str], is_active: Optional[bool]) -> PaginatedStageTypes:
        cache_params = {
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "order_dir": order_dir,
            "name": name,
            "is_active": is_active
        }
        cached = cache.get("stage_types", cache_params)
        if cached:
            self.logger.info(f"[CACHE] get_stage_types: params={cache_params}")
            return cached
        self.logger.info(f"[DB] get_stage_types: params={cache_params}")
        query = self.db.query(StageType)
        if name:
            query = query.filter(StageType.name.ilike(f"%{name}%"))
        if is_active is not None:
            query = query.filter(StageType.is_active == is_active)
        if hasattr(StageType, order_by):
            order_col = getattr(StageType, order_by)
            if order_dir == "desc":
                order_col = order_col.desc()
            else:
                order_col = order_col.asc()
            query = query.order_by(order_col)
        total = query.count()
        items = query.offset(offset).limit(limit).all()
        result = PaginatedStageTypes(
            total=total,
            count=len(items),
            offset=offset,
            limit=limit,
            items=[StageTypeRead.model_validate(st) for st in items]
        )
        cache.set("stage_types", cache_params, result)
        return result

    def get_active_stage_types(self, actor: Any) -> List[StageTypeRead]:
        stage_types = self.db.query(StageType).filter(StageType.is_active == True).order_by(StageType.created_at).all()
        return [StageTypeRead.model_validate(st) for st in stage_types]

    def get_stage_type(self, stage_type_id: str, actor: Any) -> StageTypeRead:
        uuid = UUID(stage_type_id)
        stage_type = self.db.query(StageType).get(uuid)
        if not stage_type:
            raise HTTPException(status_code=404, detail="Tipo de etapa não encontrado")
        return StageTypeRead.model_validate(stage_type)

    def create_stage_type(self, stage_type_data: StageTypeCreate, admin_user: User) -> StageTypeRead:
        if self.stage_type_exists(stage_type_data.name):
            raise HTTPException(
                status_code=400,
                detail="Já existe um tipo de etapa com este nome"
            )
        stage_type = StageType(**stage_type_data.model_dump())
        self.db.add(stage_type)
        self.db.commit()
        self.db.refresh(stage_type)
        cache.invalidate("stage_types")
        cache.invalidate("dashboard")
        return StageTypeRead.model_validate(stage_type)

    def update_stage_type(self, stage_type_id: str, stage_type_data: StageTypeUpdate, admin_user: User) -> StageTypeRead:
        uuid = UUID(stage_type_id)
        if stage_type_data.name and self.stage_type_exists(stage_type_data.name, uuid):
            raise HTTPException(
                status_code=400,
                detail="Já existe um tipo de etapa com este nome"
            )
        stage_type = self.db.query(StageType).get(uuid)
        if not stage_type:
            raise HTTPException(status_code=404, detail="Tipo de etapa não encontrado")
        for field, value in stage_type_data.model_dump(exclude_unset=True).items():
            setattr(stage_type, field, value)
        self.db.commit()
        self.db.refresh(stage_type)
        cache.invalidate("stage_types")
        cache.invalidate("dashboard")
        return StageTypeRead.model_validate(stage_type)

    def delete_stage_type(self, stage_type_id: str, admin_user: User) -> Dict[str, str]:
        uuid = UUID(stage_type_id)
        stage_type = self.db.query(StageType).get(uuid)
        if not stage_type:
            raise HTTPException(status_code=404, detail="Tipo de etapa não encontrado")
        stage_type.is_active = False
        self.db.commit()
        cache.invalidate("stage_types")
        cache.invalidate("dashboard")
        return {"message": "Tipo de etapa desativado com sucesso"}

    def stage_type_exists(self, name, exclude_id=None):
        query = self.db.query(StageType).filter(StageType.name == name)
        if exclude_id:
            query = query.filter(StageType.id != exclude_id)
        return self.db.query(query.exists()).scalar()
