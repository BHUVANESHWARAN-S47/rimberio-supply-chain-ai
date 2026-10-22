import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Integer, ForeignKey, 
    CheckConstraint, Index, DateTime
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base, GUID, TimestampMixin

class RFQDB(Base, TimestampMixin):
    __tablename__ = "rfqs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    rfq_number = Column(String(50), unique=True, nullable=False, index=True)
    buyer_id = Column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(50), default="OPEN", nullable=False, index=True)
    issue_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    response_deadline = Column(DateTime, nullable=True)
    required_delivery_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    buyer = relationship("UserDB", back_populates="rfqs")
    items = relationship("RFQItemDB", back_populates="rfq", cascade="all, delete-orphan")
    quotations = relationship("QuotationDB", back_populates="rfq")
    negotiations = relationship("NegotiationDB", back_populates="rfq")

class RFQItemDB(Base):
    __tablename__ = "rfq_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_rfq_qty_positive"),
        CheckConstraint("target_price > 0", name="check_rfq_target_price_positive"),
        CheckConstraint("required_delivery_days > 0", name="check_rfq_delivery_days_positive"),
        Index("idx_rfq_items_rfq", "rfq_id"),
        Index("idx_rfq_items_prod", "product_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    rfq_id = Column(GUID, ForeignKey("rfqs.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    target_price = Column(Float, nullable=False)
    required_quality = Column(Float, default=90.0, nullable=False)
    required_delivery_days = Column(Integer, default=14, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    rfq = relationship("RFQDB", back_populates="items")
    product = relationship("ProductDB", back_populates="rfq_items")

class QuotationDB(Base, TimestampMixin):
    __tablename__ = "quotations"
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="check_quotation_amount_positive"),
        Index("idx_quotation_supplier", "supplier_id"),
        Index("idx_quotation_rfq", "rfq_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    rfq_id = Column(GUID, ForeignKey("rfqs.id"), nullable=True)
    supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=False)
    quotation_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(String(50), default="SUBMITTED", nullable=False) # SUBMITTED, UNDER_REVIEW, ACCEPTED, REJECTED, SUPERSEDED
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    valid_until = Column(DateTime, nullable=True)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    payment_terms = Column(String(50), default="Net 30", nullable=False)
    notes = Column(Text, nullable=True)

    rfq = relationship("RFQDB", back_populates="quotations")
    supplier = relationship("SupplierDB", back_populates="quotations")
    items = relationship("QuotationItemDB", back_populates="quotation", cascade="all, delete-orphan")
    negotiations = relationship("NegotiationDB", back_populates="quotation")

class QuotationItemDB(Base):
    __tablename__ = "quotation_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_quotation_qty_positive"),
        CheckConstraint("unit_price >= 0", name="check_quotation_unit_price_positive"),
        CheckConstraint("delivery_days > 0", name="check_quotation_delivery_days_positive"),
        CheckConstraint("quality_level >= 0 AND quality_level <= 100", name="check_quotation_quality_bounds"),
        Index("idx_quotation_items_quotation", "quotation_id"),
        Index("idx_quotation_items_product", "product_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    quotation_id = Column(GUID, ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    quality_level = Column(Float, default=90.0, nullable=False)
    delivery_days = Column(Integer, nullable=False)
    minimum_order_quantity = Column(Integer, default=100, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    quotation = relationship("QuotationDB", back_populates="items")
    product = relationship("ProductDB")

class PurchaseOrderDB(Base, TimestampMixin):
    __tablename__ = "purchase_orders"
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="check_po_total_positive"),
        Index("idx_po_supplier", "supplier_id"),
        Index("idx_po_buyer", "buyer_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    po_number = Column(String(50), unique=True, nullable=False, index=True)
    supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=False)
    buyer_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="ISSUED", nullable=False) # ISSUED, ACKNOWLEDGED, SHIPPED, DELIVERED, CANCELLED
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    expected_delivery_date = Column(DateTime, nullable=False)
    actual_delivery_date = Column(DateTime, nullable=True)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)

    supplier = relationship("SupplierDB", back_populates="purchase_orders")
    buyer = relationship("UserDB", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItemDB", back_populates="purchase_order", cascade="all, delete-orphan")
    shipments = relationship("ShipmentDB", back_populates="purchase_order")
    performances = relationship("SupplierPerformanceDB", back_populates="purchase_order")
    inspections = relationship("QualityInspectionDB", back_populates="purchase_order")

class PurchaseOrderItemDB(Base):
    __tablename__ = "purchase_order_items"
    __table_args__ = (
        CheckConstraint("quantity_ordered > 0", name="check_po_ordered_qty_positive"),
        CheckConstraint("quantity_received >= 0", name="check_po_received_qty_positive"),
        CheckConstraint("unit_price >= 0", name="check_po_item_price_positive"),
        CheckConstraint("defective_quantity <= quantity_received", name="check_po_defects_lte_received"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    purchase_order_id = Column(GUID, ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(GUID, ForeignKey("products.id"), nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    quantity_received = Column(Integer, default=0, nullable=False)
    unit_price = Column(Float, nullable=False)
    defective_quantity = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    purchase_order = relationship("PurchaseOrderDB", back_populates="items")
    product = relationship("ProductDB")
