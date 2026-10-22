from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from backend.app.database.repositories.base_repository import BaseRepository
from backend.app.database.models.customer import (
    CustomerOrderDB, CustomerOrderItemDB, CustomerImpactDB, CustomerNotificationDB
)

class CustomerOrderRepository(BaseRepository[CustomerOrderDB]):
    def __init__(self, db: Session):
        super().__init__(CustomerOrderDB, db)

    def get_by_order_number(self, order_number: str) -> Optional[CustomerOrderDB]:
        return self.db.query(CustomerOrderDB).filter(CustomerOrderDB.order_number == order_number).first()

    def get_by_customer(self, customer_id, skip: int = 0, limit: int = 100) -> List[CustomerOrderDB]:
        return (
            self.db.query(CustomerOrderDB)
            .filter(CustomerOrderDB.customer_id == customer_id)
            .offset(skip).limit(limit).all()
        )

class CustomerImpactRepository(BaseRepository[CustomerImpactDB]):
    def __init__(self, db: Session):
        super().__init__(CustomerImpactDB, db)

    def get_by_simulation(self, simulation_run_id) -> List[CustomerImpactDB]:
        return (
            self.db.query(CustomerImpactDB)
            .options(joinedload(CustomerImpactDB.customer))
            .filter(CustomerImpactDB.simulation_run_id == simulation_run_id)
            .all()
        )

class CustomerNotificationRepository(BaseRepository[CustomerNotificationDB]):
    def __init__(self, db: Session):
        super().__init__(CustomerNotificationDB, db)

    def get_pending_notifications(self, skip: int = 0, limit: int = 50) -> List[CustomerNotificationDB]:
        return (
            self.db.query(CustomerNotificationDB)
            .filter(CustomerNotificationDB.status == "QUEUED")
            .offset(skip).limit(limit).all()
        )
