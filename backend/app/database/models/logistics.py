import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, ForeignKey, CheckConstraint, Index, DateTime
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base, GUID

class ShipmentDB(Base):
    __tablename__ = "shipments"
    __table_args__ = (
        CheckConstraint("shipping_cost >= 0", name="check_shipment_cost_positive"),
        CheckConstraint("distance >= 0", name="check_shipment_distance_positive"),
        Index("idx_shipment_po", "purchase_order_id"),
        Index("idx_shipment_carrier", "carrier_id"),
        Index("idx_shipment_status", "status"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    shipment_number = Column(String(50), unique=True, nullable=False, index=True)
    purchase_order_id = Column(GUID, ForeignKey("purchase_orders.id"), nullable=False)
    supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=False)
    carrier_id = Column(GUID, ForeignKey("carriers.id"), nullable=False)
    origin = Column(String(150), nullable=False)
    destination = Column(String(150), nullable=False)
    planned_departure = Column(DateTime, nullable=False)
    actual_departure = Column(DateTime, nullable=True)
    planned_arrival = Column(DateTime, nullable=False)
    actual_arrival = Column(DateTime, nullable=True)
    status = Column(String(50), default="IN_TRANSIT", nullable=False) # IN_TRANSIT, DELIVERED, DELAYED, EXCEPTION
    shipping_cost = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)
    delay_reason = Column(String(255), nullable=True)
    expected_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    purchase_order = relationship("PurchaseOrderDB", back_populates="shipments")
    supplier = relationship("SupplierDB")
    carrier = relationship("CarrierDB", back_populates="shipments")
    events = relationship("ShipmentEventDB", back_populates="shipment", cascade="all, delete-orphan")

class ShipmentEventDB(Base):
    __tablename__ = "shipment_events"
    __table_args__ = (
        Index("idx_shipment_events_shipment", "shipment_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    shipment_id = Column(GUID, ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), nullable=False) # DEPARTURE, CHECKPOINT, DELAY_ALERT, CUSTOMS_CLEARANCE, ARRIVAL
    location = Column(String(150), nullable=False)
    event_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    description = Column(Text, nullable=True)

    shipment = relationship("ShipmentDB", back_populates="events")

class LogisticsEvaluationDB(Base):
    __tablename__ = "logistics_evaluations"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    carrier_id = Column(GUID, ForeignKey("carriers.id"), nullable=False)
    evaluation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    on_time_delivery_rate = Column(Float, nullable=False)
    damage_incident_rate = Column(Float, default=0.0, nullable=False)
    cost_efficiency_score = Column(Float, nullable=False)
    composite_logistics_score = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)

    carrier = relationship("CarrierDB")
