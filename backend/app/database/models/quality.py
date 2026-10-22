import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Integer, ForeignKey, CheckConstraint, Index, DateTime
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base, GUID

class QualityInspectionDB(Base):
    __tablename__ = "quality_inspections"
    __table_args__ = (
        CheckConstraint("quantity_inspected > 0", name="check_insp_qty_positive"),
        CheckConstraint("quantity_passed >= 0", name="check_insp_passed_positive"),
        CheckConstraint("quantity_failed >= 0", name="check_insp_failed_positive"),
        CheckConstraint("quantity_passed + quantity_failed = quantity_inspected", name="check_insp_sum_match"),
        CheckConstraint("quality_score >= 0 AND quality_score <= 100", name="check_insp_score_bounds"),
        Index("idx_insp_supplier", "supplier_id"),
        Index("idx_insp_product", "product_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=False)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=False)
    purchase_order_id = Column(GUID, ForeignKey("purchase_orders.id"), nullable=True)
    inspection_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    quantity_inspected = Column(Integer, nullable=False)
    quantity_passed = Column(Integer, nullable=False)
    quantity_failed = Column(Integer, default=0, nullable=False)
    quality_score = Column(Float, nullable=False)
    defect_rate = Column(Float, default=0.0, nullable=False)
    notes = Column(Text, nullable=True)

    supplier = relationship("SupplierDB")
    product = relationship("ProductDB")
    purchase_order = relationship("PurchaseOrderDB", back_populates="inspections")

class QualityIncidentDB(Base):
    __tablename__ = "quality_incidents"
    __table_args__ = (
        Index("idx_incident_supplier", "supplier_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=False)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=False)
    purchase_order_id = Column(GUID, ForeignKey("purchase_orders.id"), nullable=True)
    incident_type = Column(String(100), nullable=False)
    severity = Column(String(50), default="MEDIUM", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    description = Column(Text, nullable=False)
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    supplier = relationship("SupplierDB")
    product = relationship("ProductDB")
