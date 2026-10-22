import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Integer, ForeignKey, CheckConstraint, Index, DateTime
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base, GUID

class CustomerOrderDB(Base):
    __tablename__ = "customer_orders"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_cust_order_qty_positive"),
        CheckConstraint("unit_price >= 0", name="check_cust_order_price_positive"),
        CheckConstraint("total_amount >= 0", name="check_cust_order_total_positive"),
        Index("idx_cust_order_customer", "customer_id"),
        Index("idx_cust_order_prod", "product_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(GUID, ForeignKey("customers.id"), nullable=False)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    promised_delivery_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="SCHEDULED", nullable=False) # SCHEDULED, IN_FULFILLMENT, DELAYED_ALERT, DELIVERED, CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("CustomerDB", back_populates="orders")
    product = relationship("ProductDB")
    items = relationship("CustomerOrderItemDB", back_populates="customer_order", cascade="all, delete-orphan")
    impacts = relationship("CustomerImpactDB", back_populates="affected_order")

class CustomerOrderItemDB(Base):
    __tablename__ = "customer_order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_cust_item_qty_positive"),
        CheckConstraint("unit_price >= 0", name="check_cust_item_price_positive"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    customer_order_id = Column(GUID, ForeignKey("customer_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer_order = relationship("CustomerOrderDB", back_populates="items")
    product = relationship("ProductDB")

class CustomerImpactDB(Base):
    __tablename__ = "customer_impacts"
    __table_args__ = (
        CheckConstraint("revenue_at_risk >= 0", name="check_impact_revenue_positive"),
        Index("idx_cust_impact_sim", "simulation_run_id"),
        Index("idx_cust_impact_cust", "customer_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    simulation_run_id = Column(GUID, ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(GUID, ForeignKey("customers.id"), nullable=False)
    affected_order_id = Column(GUID, ForeignKey("customer_orders.id"), nullable=True)
    supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=True)
    affected_product_id = Column(GUID, ForeignKey("products.id"), nullable=False)
    expected_delay_days = Column(Integer, default=0, nullable=False)
    availability_change = Column(Float, default=0.0, nullable=False) # e.g. -5.0%
    service_level_change = Column(Float, default=0.0, nullable=False) # e.g. -2.5%
    revenue_at_risk = Column(Float, default=0.0, nullable=False)
    impact_level = Column(String(50), default="LOW", nullable=False) # NONE, LOW, MEDIUM, HIGH, CRITICAL
    reasoning = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    simulation_run = relationship("SimulationRunDB", back_populates="customer_impacts")
    customer = relationship("CustomerDB", back_populates="impacts")
    affected_order = relationship("CustomerOrderDB", back_populates="impacts")
    supplier = relationship("SupplierDB")
    affected_product = relationship("ProductDB")
    notifications = relationship("CustomerNotificationDB", back_populates="impact")

class CustomerNotificationDB(Base):
    __tablename__ = "customer_notifications"
    __table_args__ = (
        Index("idx_cust_notif_cust", "customer_id"),
        Index("idx_cust_notif_status", "status"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    customer_id = Column(GUID, ForeignKey("customers.id"), nullable=False)
    impact_id = Column(GUID, ForeignKey("customer_impacts.id"), nullable=True)
    notification_type = Column(String(50), default="SWITCHING_ADVISORY", nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(50), default="INFO", nullable=False) # INFO, WARNING, URGENT
    status = Column(String(50), default="QUEUED", nullable=False) # QUEUED, SENT, READ, DISMISSED
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("CustomerDB", back_populates="notifications")
    impact = relationship("CustomerImpactDB", back_populates="notifications")


class SupportTicketDB(Base):
    __tablename__ = "support_tickets"
    __table_args__ = (
        Index("idx_ticket_cust", "customer_id"),
        Index("idx_ticket_status", "status"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    customer_id = Column(GUID, ForeignKey("customers.id"), nullable=False)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="OPEN", nullable=False)  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("CustomerDB")

