import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Integer, ForeignKey, CheckConstraint, Index, DateTime, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base, GUID

class SimulationRunDB(Base):
    __tablename__ = "simulation_runs"
    __table_args__ = (
        Index("idx_sim_run_supplier", "supplier_id"),
        Index("idx_sim_run_product", "product_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    run_id = Column(String(100), unique=True, nullable=False, index=True)
    trigger_type = Column(String(50), default="MANUAL_EVALUATION", nullable=False) # MANUAL_EVALUATION, DISRUPTION_ALERT, RFQ_EVALUATION
    supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=True)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=True)
    baseline_reference = Column(String(100), nullable=True)
    created_by = Column(String(100), default="SYSTEM_TWIN", nullable=False)
    status = Column(String(50), default="COMPLETED", nullable=False) # RUNNING, COMPLETED, FAILED
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    scenarios = relationship("SimulationScenarioDB", back_populates="run", cascade="all, delete-orphan")
    comparisons = relationship("SupplierComparisonDB", back_populates="simulation_run")
    decision = relationship("AdaptiveDecisionDB", back_populates="simulation_run", uselist=False)
    customer_impacts = relationship("CustomerImpactDB", back_populates="simulation_run")

class SimulationScenarioDB(Base):
    __tablename__ = "simulation_scenarios"
    __table_args__ = (
        Index("idx_sim_scenario_run", "simulation_run_id"),
        Index("idx_sim_scenario_type", "scenario_type"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    simulation_run_id = Column(GUID, ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False)
    scenario_type = Column(String(50), nullable=False)
    # NORMAL, HIGH_DEMAND, LOW_DEMAND, SUPPLIER_DELAY, TRANSPORT_DISRUPTION, SUPPLY_SHORTAGE, PRICE_INCREASE, INVENTORY_SHORTAGE
    description = Column(Text, nullable=True)
    assumptions = Column(JSON, nullable=True)

    run = relationship("SimulationRunDB", back_populates="scenarios")
    results = relationship("SimulationResultDB", back_populates="scenario", cascade="all, delete-orphan")

class SimulationResultDB(Base):
    __tablename__ = "simulation_results"
    __table_args__ = (
        CheckConstraint("candidate_price >= 0", name="check_sim_price_positive"),
        CheckConstraint("predicted_cost >= 0", name="check_sim_pred_cost_positive"),
        CheckConstraint("predicted_stockout_rate >= 0 AND predicted_stockout_rate <= 1.0", name="check_sim_stockout_rate_bounds"),
        CheckConstraint("predicted_service_level >= 0 AND predicted_service_level <= 100", name="check_sim_service_level_bounds"),
        Index("idx_sim_res_scenario", "simulation_scenario_id"),
        Index("idx_sim_res_supplier", "candidate_supplier_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    simulation_scenario_id = Column(GUID, ForeignKey("simulation_scenarios.id", ondelete="CASCADE"), nullable=False)
    candidate_supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=False)
    candidate_price = Column(Float, nullable=False)
    candidate_delivery_days = Column(Integer, nullable=False)
    predicted_cost = Column(Float, nullable=False)
    predicted_profit = Column(Float, nullable=False)
    predicted_inventory = Column(Integer, nullable=False)
    predicted_delivery_delay = Column(Float, default=0.0, nullable=False)
    predicted_stockout_rate = Column(Float, default=0.0, nullable=False)
    predicted_risk = Column(Float, default=20.0, nullable=False)
    predicted_service_level = Column(Float, default=95.0, nullable=False)
    predicted_customer_impact = Column(Float, default=0.0, nullable=False)
    prediction_confidence = Column(Float, default=0.92, nullable=False)
    model_version = Column(String(50), default="CNT_SIMULATOR_V2", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    scenario = relationship("SimulationScenarioDB", back_populates="results")
    candidate_supplier = relationship("SupplierDB")
    actuals = relationship("PredictionActualDB", back_populates="simulation_result")
