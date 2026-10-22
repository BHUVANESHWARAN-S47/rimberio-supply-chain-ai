import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, ForeignKey, CheckConstraint, Index, DateTime, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base, GUID

class RiskEventDB(Base):
    __tablename__ = "risk_events"
    __table_args__ = (
        CheckConstraint("probability >= 0 AND probability <= 1.0", name="check_risk_prob_bounds"),
        Index("idx_risk_event_supplier", "supplier_id"),
        Index("idx_risk_event_type", "event_type"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=True)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=True)
    event_type = Column(String(100), nullable=False) 
    # supplier_delay, capacity_shortage, quality_failure, transport_disruption, inventory_shortage, price_increase, demand_spike
    probability = Column(Float, default=0.2, nullable=False)
    severity = Column(String(50), default="MEDIUM", nullable=False) # LOW, MEDIUM, HIGH, SEVERE
    impact = Column(Float, default=50.0, nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=False)
    source = Column(String(100), default="TELEMETRY_MONITOR", nullable=False)

    supplier = relationship("SupplierDB", back_populates="risk_events")
    product = relationship("ProductDB")

class RiskAssessmentDB(Base):
    __tablename__ = "risk_assessments"
    __table_args__ = (
        CheckConstraint("overall_risk >= 0 AND overall_risk <= 100", name="check_overall_risk_bounds"),
        Index("idx_risk_assessment_supplier", "supplier_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=False)
    assessment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    delivery_risk = Column(Float, default=20.0, nullable=False)
    quality_risk = Column(Float, default=15.0, nullable=False)
    financial_risk = Column(Float, default=10.0, nullable=False)
    capacity_risk = Column(Float, default=25.0, nullable=False)
    logistics_risk = Column(Float, default=30.0, nullable=False)
    inventory_risk = Column(Float, default=15.0, nullable=False)
    overall_risk = Column(Float, nullable=False)
    confidence = Column(Float, default=0.90, nullable=False)
    model_version = Column(String(50), default="RISK_ENGINE_V1", nullable=False)
    reasoning = Column(JSON, nullable=True)

    supplier = relationship("SupplierDB", back_populates="risk_assessments")
