import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Integer, ForeignKey, CheckConstraint, Index, DateTime, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base, GUID

class SupplierComparisonDB(Base):
    __tablename__ = "supplier_comparisons"
    __table_args__ = (
        CheckConstraint("rank >= 1", name="check_comp_rank_positive"),
        Index("idx_sup_comp_run", "simulation_run_id"),
        Index("idx_sup_comp_supplier", "supplier_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    simulation_run_id = Column(GUID, ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False)
    supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=False)
    price_score = Column(Float, nullable=False)
    quality_score = Column(Float, nullable=False)
    delivery_score = Column(Float, nullable=False)
    reliability_score = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    logistics_score = Column(Float, nullable=False)
    customer_impact_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    simulation_run = relationship("SimulationRunDB", back_populates="comparisons")
    supplier = relationship("SupplierDB")

class AdaptiveDecisionDB(Base):
    __tablename__ = "adaptive_decisions"
    __table_args__ = (
        CheckConstraint("confidence >= 0 AND confidence <= 1.0", name="check_dec_confidence_bounds"),
        Index("idx_adapt_dec_run", "simulation_run_id"),
        Index("idx_adapt_dec_type", "decision_type"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    simulation_run_id = Column(GUID, ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False)
    selected_supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=False)
    decision_type = Column(String(50), nullable=False) # RETAIN, NEGOTIATE, SWITCH
    confidence = Column(Float, default=0.95, nullable=False)
    reasoning = Column(Text, nullable=False)
    decision_factors = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    simulation_run = relationship("SimulationRunDB", back_populates="decision")
    selected_supplier = relationship("SupplierDB")
