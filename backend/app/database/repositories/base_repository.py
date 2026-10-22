from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func
from backend.app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Generic repository implementing standard persistence patterns."""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, entity_id: Any) -> Optional[ModelType]:
        """Fetches a single entity by its primary key."""
        return self.db.query(self.model).filter(self.model.id == entity_id).first()

    def list(self, skip: int = 0, limit: int = 100, **filters) -> List[ModelType]:
        """Lists entities with optional filtering and pagination."""
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()

    def create(self, entity: ModelType) -> ModelType:
        """Persists a new entity to the database."""
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def bulk_create(self, entities: List[ModelType]) -> List[ModelType]:
        """Persists multiple entities in a single transaction."""
        self.db.add_all(entities)
        self.db.commit()
        return entities

    def update(self, entity_id: Any, values: Dict[str, Any]) -> Optional[ModelType]:
        """Updates entity attributes."""
        entity = self.get_by_id(entity_id)
        if not entity:
            return None
        for key, val in values.items():
            if hasattr(entity, key):
                setattr(entity, key, val)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity_id: Any) -> bool:
        """Deletes an entity by primary key."""
        entity = self.get_by_id(entity_id)
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True

    def count(self, **filters) -> int:
        """Counts entities matching filters."""
        query = self.db.query(func.count(self.model.id))
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.scalar() or 0
