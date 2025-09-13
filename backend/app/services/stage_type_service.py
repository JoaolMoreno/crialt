from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from ..models.stage_type import StageType
from ..schemas.stage_type import StageTypeCreate, StageTypeUpdate


class StageTypeService:
    def __init__(self, db: Session):
        self.db = db

    def get_stage_type(self, stage_type_id: UUID) -> Optional[StageType]:
        return self.db.query(StageType).filter(StageType.id == stage_type_id).first()

    def get_stage_types(
        self,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[StageType], int]:
        query = self.db.query(StageType)

        if name:
            query = query.filter(StageType.name.ilike(f"%{name}%"))
        if is_active is not None:
            query = query.filter(StageType.is_active == is_active)

        total = query.count()
        stage_types = query.offset(skip).limit(limit).all()

        return stage_types, total

    def create_stage_type(self, stage_type_data: StageTypeCreate) -> StageType:
        stage_type_dict = stage_type_data.model_dump()
        stage_type = StageType(**stage_type_dict)

        self.db.add(stage_type)
        self.db.commit()
        self.db.refresh(stage_type)

        return stage_type

    def update_stage_type(
        self,
        stage_type_id: UUID,
        stage_type_data: StageTypeUpdate
    ) -> Optional[StageType]:
        stage_type = self.get_stage_type(stage_type_id)
        if not stage_type:
            return None

        update_data = stage_type_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(stage_type, field, value)

        self.db.commit()
        self.db.refresh(stage_type)

        return stage_type

    def delete_stage_type(self, stage_type_id: UUID) -> bool:
        stage_type = self.get_stage_type(stage_type_id)
        if not stage_type:
            return False

        stage_type.is_active = False
        self.db.commit()

        return True

    def get_active_stage_types(self) -> List[StageType]:
        return self.db.query(StageType).filter(StageType.is_active == True).all()

    def stage_type_exists(self, name: str, exclude_id: Optional[UUID] = None) -> bool:
        query = self.db.query(StageType).filter(StageType.name == name)
        if exclude_id:
            query = query.filter(StageType.id != exclude_id)
        return query.first() is not None
