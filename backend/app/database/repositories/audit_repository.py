from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.database.repositories.base_repository import BaseRepository
from backend.app.database.models.audit import (
    AgentExecutionDB, AgentMessageDB, AuditLogDB, SystemEventDB, KaggleStagingDB
)

class AgentExecutionRepository(BaseRepository[AgentExecutionDB]):
    def __init__(self, db: Session):
        super().__init__(AgentExecutionDB, db)

    def get_by_session(self, session_id: str) -> List[AgentExecutionDB]:
        return (
            self.db.query(AgentExecutionDB)
            .filter(AgentExecutionDB.session_id == session_id)
            .order_by(AgentExecutionDB.created_at.asc())
            .all()
        )

class AuditLogRepository(BaseRepository[AuditLogDB]):
    def __init__(self, db: Session):
        super().__init__(AuditLogDB, db)

    def log_action(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        user_id: Optional[Any] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLogDB:
        entry = AuditLogDB(
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            user_id=user_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address
        )
        return self.create(entry)

class KaggleStagingRepository(BaseRepository[KaggleStagingDB]):
    def __init__(self, db: Session):
        super().__init__(KaggleStagingDB, db)

    def get_by_batch(self, batch_id: str) -> List[KaggleStagingDB]:
        return (
            self.db.query(KaggleStagingDB)
            .filter(KaggleStagingDB.import_batch_id == batch_id)
            .all()
        )
