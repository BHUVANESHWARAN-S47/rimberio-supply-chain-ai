from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from backend.app.database.repositories.base_repository import BaseRepository
from backend.app.database.models.procurement import (
    RFQDB, RFQItemDB, QuotationDB, QuotationItemDB, PurchaseOrderDB, PurchaseOrderItemDB
)

class RFQRepository(BaseRepository[RFQDB]):
    def __init__(self, db: Session):
        super().__init__(RFQDB, db)

    def get_by_number(self, rfq_number: str) -> Optional[RFQDB]:
        return self.db.query(RFQDB).filter(RFQDB.rfq_number == rfq_number).first()

    def get_with_items(self, rfq_id) -> Optional[RFQDB]:
        return (
            self.db.query(RFQDB)
            .options(joinedload(RFQDB.items).joinedload(RFQItemDB.product))
            .filter(RFQDB.id == rfq_id)
            .first()
        )

class QuotationRepository(BaseRepository[QuotationDB]):
    def __init__(self, db: Session):
        super().__init__(QuotationDB, db)

    def get_by_number(self, quotation_number: str) -> Optional[QuotationDB]:
        return self.db.query(QuotationDB).filter(QuotationDB.quotation_number == quotation_number).first()

    def get_by_supplier(self, supplier_id, skip: int = 0, limit: int = 100) -> List[QuotationDB]:
        return (
            self.db.query(QuotationDB)
            .filter(QuotationDB.supplier_id == supplier_id)
            .offset(skip).limit(limit).all()
        )

class PurchaseOrderRepository(BaseRepository[PurchaseOrderDB]):
    def __init__(self, db: Session):
        super().__init__(PurchaseOrderDB, db)

    def get_by_po_number(self, po_number: str) -> Optional[PurchaseOrderDB]:
        return self.db.query(PurchaseOrderDB).filter(PurchaseOrderDB.po_number == po_number).first()
