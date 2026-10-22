import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, ForeignKey, CheckConstraint, Index, DateTime
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base, GUID

class DemandHistoryDB(Base):
    __tablename__ = "demand_history"
    __table_args__ = (
        CheckConstraint("quantity_demanded >= 0", name="check_demand_qty_positive"),
        CheckConstraint("quantity_sold >= 0", name="check_sold_qty_positive"),
        Index("idx_demand_hist_prod", "product_id"),
        Index("idx_demand_hist_date", "date"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(GUID, ForeignKey("warehouses.id"), nullable=True)
    date = Column(DateTime, nullable=False)
    quantity_demanded = Column(Integer, nullable=False)
    quantity_sold = Column(Integer, nullable=False)
    source = Column(String(50), default="ACTUAL_SALES", nullable=False) # ACTUAL_SALES, POS, ERP

    product = relationship("ProductDB")
    warehouse = relationship("WarehouseDB")

class DemandForecastDB(Base):
    __tablename__ = "demand_forecasts"
    __table_args__ = (
        CheckConstraint("predicted_demand >= 0", name="check_predicted_demand_positive"),
        Index("idx_demand_fc_prod", "product_id"),
        Index("idx_demand_fc_date", "forecast_date"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(GUID, ForeignKey("warehouses.id"), nullable=True)
    forecast_date = Column(DateTime, nullable=False)
    predicted_demand = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)
    model_version = Column(String(50), default="ARIMA_ENSEMBLE_V1", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("ProductDB")
    warehouse = relationship("WarehouseDB")
