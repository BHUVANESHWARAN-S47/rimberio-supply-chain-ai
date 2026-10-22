import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, ForeignKey, CheckConstraint, Index, DateTime, UniqueConstraint
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base, GUID

class InventoryDB(Base):
    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "product_id", name="uq_warehouse_product_inventory"),
        CheckConstraint("quantity_on_hand >= 0", name="check_inv_on_hand_positive"),
        CheckConstraint("reserved_quantity >= 0", name="check_inv_reserved_positive"),
        CheckConstraint("available_quantity >= 0", name="check_inv_available_positive"),
        Index("idx_inventory_warehouse", "warehouse_id"),
        Index("idx_inventory_product", "product_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    warehouse_id = Column(GUID, ForeignKey("warehouses.id"), nullable=False)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=False)
    quantity_on_hand = Column(Integer, default=0, nullable=False)
    reserved_quantity = Column(Integer, default=0, nullable=False)
    available_quantity = Column(Integer, default=0, nullable=False)
    safety_stock = Column(Integer, default=500, nullable=False)
    reorder_point = Column(Integer, default=1000, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    warehouse = relationship("WarehouseDB", back_populates="inventory_items")
    product = relationship("ProductDB", back_populates="inventory_items")

class InventoryMovementDB(Base):
    __tablename__ = "inventory_movements"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_inv_mov_qty_positive"),
        Index("idx_inv_mov_prod", "product_id"),
        Index("idx_inv_mov_wh", "warehouse_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    warehouse_id = Column(GUID, ForeignKey("warehouses.id"), nullable=False)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=False)
    movement_type = Column(String(50), nullable=False) # INBOUND, OUTBOUND, TRANSFER, ADJUSTMENT
    quantity = Column(Integer, nullable=False)
    reference_type = Column(String(50), nullable=True) # PURCHASE_ORDER, CUSTOMER_ORDER, RETURN
    reference_id = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    warehouse = relationship("WarehouseDB")
    product = relationship("ProductDB")

class InventorySnapshotDB(Base):
    __tablename__ = "inventory_snapshots"
    __table_args__ = (
        Index("idx_inv_snap_prod", "product_id"),
        Index("idx_inv_snap_date", "snapshot_date"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    warehouse_id = Column(GUID, ForeignKey("warehouses.id"), nullable=False)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=False)
    quantity_on_hand = Column(Integer, nullable=False)
    snapshot_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    warehouse = relationship("WarehouseDB")
    product = relationship("ProductDB")
