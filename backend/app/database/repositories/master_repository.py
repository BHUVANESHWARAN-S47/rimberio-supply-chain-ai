from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from backend.app.database.repositories.base_repository import BaseRepository
from backend.app.database.models.master import (
    SupplierDB, ProductDB, SupplierProductDB, CustomerDB, WarehouseDB, CarrierDB, UserDB, RoleDB
)

class SupplierRepository(BaseRepository[SupplierDB]):
    def __init__(self, db: Session):
        super().__init__(SupplierDB, db)

    def get_by_code(self, supplier_code: str) -> Optional[SupplierDB]:
        return self.db.query(SupplierDB).filter(SupplierDB.supplier_code == supplier_code).first()

    def get_with_products(self, supplier_id) -> Optional[SupplierDB]:
        return (
            self.db.query(SupplierDB)
            .options(joinedload(SupplierDB.products).joinedload(SupplierProductDB.product))
            .filter(SupplierDB.id == supplier_id)
            .first()
        )

    def get_active_suppliers(self, skip: int = 0, limit: int = 100) -> List[SupplierDB]:
        return self.db.query(SupplierDB).filter(SupplierDB.status == "ACTIVE").offset(skip).limit(limit).all()

class ProductRepository(BaseRepository[ProductDB]):
    def __init__(self, db: Session):
        super().__init__(ProductDB, db)

    def get_by_sku(self, sku: str) -> Optional[ProductDB]:
        return self.db.query(ProductDB).filter(ProductDB.sku == sku).first()

    def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[ProductDB]:
        return self.db.query(ProductDB).filter(ProductDB.category == category).offset(skip).limit(limit).all()

class CustomerRepository(BaseRepository[CustomerDB]):
    def __init__(self, db: Session):
        super().__init__(CustomerDB, db)

    def get_by_code(self, customer_code: str) -> Optional[CustomerDB]:
        return self.db.query(CustomerDB).filter(CustomerDB.customer_code == customer_code).first()

    def get_by_priority(self, priority: str) -> List[CustomerDB]:
        return self.db.query(CustomerDB).filter(CustomerDB.priority == priority).all()

class WarehouseRepository(BaseRepository[WarehouseDB]):
    def __init__(self, db: Session):
        super().__init__(WarehouseDB, db)

    def get_by_code(self, warehouse_code: str) -> Optional[WarehouseDB]:
        return self.db.query(WarehouseDB).filter(WarehouseDB.warehouse_code == warehouse_code).first()

class CarrierRepository(BaseRepository[CarrierDB]):
    def __init__(self, db: Session):
        super().__init__(CarrierDB, db)

    def get_by_code(self, carrier_code: str) -> Optional[CarrierDB]:
        return self.db.query(CarrierDB).filter(CarrierDB.carrier_code == carrier_code).first()

class UserRepository(BaseRepository[UserDB]):
    def __init__(self, db: Session):
        super().__init__(UserDB, db)

    def get_by_email(self, email: str) -> Optional[UserDB]:
        return self.db.query(UserDB).filter(UserDB.email == email).first()
