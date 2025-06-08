from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.core.database import BaseModel

ModelType = TypeVar("Model Type", bound = BaseModel)

class CRUDBase(Generic[ModelType]):
    """CRUD object with default methods"""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a single object by ID"""
        return db.get(self.model, id)
    
    def get_multi(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        results = db.exec(statement)
        return results.all()
    
    def create(self, db: Session, *, obj_in: ModelType) -> ModelType:
        try:
            db.add(obj_in)
            db.commit()
            db.refresh(obj_in)
            return obj_in
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code = 400, datail = str(e))
        
    def update(
            self,
            db: Session,
            *,
            db_obj: ModelType,
            obj_in: Union[Dict[str, Any], ModelType]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else :
            update_data = obj_in.model_dump(exclude_unset = True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.get(self.model, id)
        if not obj:
            raise HTTPException(status_code = 404, details = "object not found")
        db.delete(obj)
        db.commit()
        return obj
    