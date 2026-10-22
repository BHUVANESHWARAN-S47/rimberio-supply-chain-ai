import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, ForeignKey, Index, DateTime
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base, GUID

class PredictionActualDB(Base):
    __tablename__ = "prediction_actuals"
    __table_args__ = (
        Index("idx_pred_act_sim", "simulation_result_id"),
        Index("idx_pred_act_supplier", "actual_supplier_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    simulation_result_id = Column(GUID, ForeignKey("simulation_results.id"), nullable=False)
    actual_supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=False)
    actual_cost = Column(Float, nullable=False)
    actual_delivery_days = Column(Integer, nullable=False)
    actual_inventory = Column(Integer, nullable=False)
    actual_stockout_rate = Column(Float, default=0.0, nullable=False)
    actual_service_level = Column(Float, default=95.0, nullable=False)
    actual_customer_impact = Column(Float, default=0.0, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    simulation_result = relationship("SimulationResultDB", back_populates="actuals")
    actual_supplier = relationship("SupplierDB")
    feedback_entries = relationship("ModelFeedbackDB", back_populates="prediction_actual", cascade="all, delete-orphan")

class ModelFeedbackDB(Base):
    __tablename__ = "model_feedback"
    __table_args__ = (
        Index("idx_model_fb_metric", "metric_name"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    prediction_actual_id = Column(GUID, ForeignKey("prediction_actuals.id", ondelete="CASCADE"), nullable=False)
    metric_name = Column(String(100), nullable=False) # cost, delivery_days, inventory, stockout_rate, service_level
    predicted_value = Column(Float, nullable=False)
    actual_value = Column(Float, nullable=False)
    error = Column(Float, nullable=False) # predicted - actual
    absolute_error = Column(Float, nullable=False) # abs(predicted - actual)
    percentage_error = Column(Float, nullable=False) # abs(predicted - actual) / actual * 100
    model_version = Column(String(50), default="CNT_SIMULATOR_V2", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    prediction_actual = relationship("PredictionActualDB", back_populates="feedback_entries")
