from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from backend.app.database.repositories.base_repository import BaseRepository
from backend.app.database.models.negotiation import (
    NegotiationDB, NegotiationRoundDB, NegotiationMessageDB
)

class NegotiationRepository(BaseRepository[NegotiationDB]):
    def __init__(self, db: Session):
        super().__init__(NegotiationDB, db)

    def get_with_rounds(self, negotiation_id) -> Optional[NegotiationDB]:
        return (
            self.db.query(NegotiationDB)
            .options(
                joinedload(NegotiationDB.rounds),
                joinedload(NegotiationDB.messages)
            )
            .filter(NegotiationDB.id == negotiation_id)
            .first()
        )

    def get_by_supplier(self, supplier_id, skip: int = 0, limit: int = 50) -> List[NegotiationDB]:
        return (
            self.db.query(NegotiationDB)
            .filter(NegotiationDB.supplier_id == supplier_id)
            .offset(skip).limit(limit).all()
        )

class NegotiationRoundRepository(BaseRepository[NegotiationRoundDB]):
    def __init__(self, db: Session):
        super().__init__(NegotiationRoundDB, db)

    def get_by_negotiation(self, negotiation_id) -> List[NegotiationRoundDB]:
        return (
            self.db.query(NegotiationRoundDB)
            .filter(NegotiationRoundDB.negotiation_id == negotiation_id)
            .order_by(NegotiationRoundDB.round_number.asc())
            .all()
        )
