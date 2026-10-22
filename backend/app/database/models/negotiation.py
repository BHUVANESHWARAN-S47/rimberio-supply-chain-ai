import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Integer, Boolean, ForeignKey, 
    CheckConstraint, Index, DateTime, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base, GUID, TimestampMixin

class NegotiationDB(Base, TimestampMixin):
    __tablename__ = "negotiations"
    __table_args__ = (
        CheckConstraint("current_round >= 1", name="check_neg_current_round_positive"),
        Index("idx_neg_supplier", "supplier_id"),
        Index("idx_neg_buyer", "buyer_id"),
        Index("idx_neg_rfq", "rfq_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    rfq_id = Column(GUID, ForeignKey("rfqs.id"), nullable=True)
    supplier_id = Column(GUID, ForeignKey("suppliers.id"), nullable=False)
    buyer_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    quotation_id = Column(GUID, ForeignKey("quotations.id"), nullable=True)
    status = Column(String(50), default="IN_PROGRESS", nullable=False) # IN_PROGRESS, AGREED, REJECTED, EXPIRED
    current_round = Column(Integer, default=1, nullable=False)
    initial_offer_id = Column(GUID, nullable=True)
    final_quotation_id = Column(GUID, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    rounds = relationship("NegotiationRoundDB", back_populates="negotiation", cascade="all, delete-orphan")
    messages = relationship("NegotiationMessageDB", back_populates="negotiation", cascade="all, delete-orphan")
    rfq = relationship("RFQDB", back_populates="negotiations")
    quotation = relationship("QuotationDB", back_populates="negotiations")
    supplier = relationship("SupplierDB")

class NegotiationRoundDB(Base):
    __tablename__ = "negotiation_rounds"
    __table_args__ = (
        CheckConstraint("round_number >= 1", name="check_neg_round_num_positive"),
        CheckConstraint("offered_price >= 0", name="check_neg_price_positive"),
        CheckConstraint("quantity > 0", name="check_neg_quantity_positive"),
        CheckConstraint("delivery_days > 0", name="check_neg_delivery_days_positive"),
        Index("idx_neg_round_neg_id", "negotiation_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    negotiation_id = Column(GUID, ForeignKey("negotiations.id", ondelete="CASCADE"), nullable=False)
    round_number = Column(Integer, nullable=False)
    actor_type = Column(String(50), nullable=False) # BUYER, SUPPLIER, SYSTEM
    actor_id = Column(String(100), nullable=False)
    offered_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    delivery_days = Column(Integer, nullable=False)
    quality_level = Column(Float, default=90.0, nullable=False)
    payment_terms = Column(String(50), default="Net 30", nullable=False)
    proposal = Column(Text, nullable=True)
    counterproposal = Column(Text, nullable=True)
    accepted = Column(Boolean, default=False, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    negotiation = relationship("NegotiationDB", back_populates="rounds")
    messages = relationship("NegotiationMessageDB", back_populates="round", cascade="all, delete-orphan")

class NegotiationMessageDB(Base):
    __tablename__ = "negotiation_messages"
    __table_args__ = (
        Index("idx_neg_msg_neg_id", "negotiation_id"),
        Index("idx_neg_msg_round_id", "round_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    negotiation_id = Column(GUID, ForeignKey("negotiations.id", ondelete="CASCADE"), nullable=False)
    round_id = Column(GUID, ForeignKey("negotiation_rounds.id", ondelete="CASCADE"), nullable=True)
    sender_type = Column(String(50), nullable=False) # BUYER, SUPPLIER, ARBITRATOR, OBSERVER
    message = Column(Text, nullable=False)
    structured_offer = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    negotiation = relationship("NegotiationDB", back_populates="messages")
    round = relationship("NegotiationRoundDB", back_populates="messages")
