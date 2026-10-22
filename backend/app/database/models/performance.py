import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Integer, Boolean, ForeignKey, 
    CheckConstraint, Index, DateTime
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base, GUID

class SupplierPerformanceDB(Base):
    __tablename__ = "supplier_performance"
    __table_args__ = (
        CheckConstraint("ordered_quantity > 0", name="check_perf_ordered_qty"),
        CheckConstraint("received_quantity >= 0", name="check_perf_received_qty"),
        CheckConstraint("defective_quantity <= received_quantity", name="check_perf_defects_lte_recv"),
        CheckConstraint("quality_score >= 0 AND quality_score <= 100", name="check_perf_quality_bounds"),
        Index("idx_perf_supplier", "supplier_id"),
        Index("idx_perf_po", "purchase_order_id"),
        Index("idx_perf_prod", "product_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=False)
    purchase_order_id = Column(GUID, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=False)
    promised_delivery_date = Column(DateTime, nullable=False)
    actual_delivery_date = Column(DateTime, nullable=False)
    ordered_quantity = Column(Integer, nullable=False)
    received_quantity = Column(Integer, nullable=False)
    defective_quantity = Column(Integer, default=0, nullable=False)
    unit_price = Column(Float, nullable=False)
    lead_time_days = Column(Integer, nullable=False)
    on_time = Column(Boolean, nullable=False)
    quality_score = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    supplier = relationship("SupplierDB", back_populates="performances")
    purchase_order = relationship("PurchaseOrderDB", back_populates="performances")
    product = relationship("ProductDB")

class SupplierEvaluationDB(Base):
    __tablename__ = "supplier_evaluations"
    __table_args__ = (
        Index("idx_eval_supplier", "supplier_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=False)
    evaluation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    overall_score = Column(Float, nullable=False)
    price_score = Column(Float, nullable=False)
    quality_score = Column(Float, nullable=False)
    delivery_score = Column(Float, nullable=False)
    reliability_score = Column(Float, nullable=False)
    evaluator_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    supplier = relationship("SupplierDB")

class SupplierRiskScoreDB(Base):
    __tablename__ = "supplier_risk_scores"
    __table_args__ = (
        Index("idx_risk_score_supplier", "supplier_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    financial_risk = Column(Float, nullable=False)
    operational_risk = Column(Float, nullable=False)
    geopolitical_risk = Column(Float, nullable=False)
    overall_risk = Column(Float, nullable=False)

    supplier = relationship("SupplierDB")
