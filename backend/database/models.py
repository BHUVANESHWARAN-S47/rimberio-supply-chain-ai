import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database.database import Base

class SupplierDB(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    tier = Column(String(100), default="Standard")
    country = Column(String(100), default="Global")
    unit_cost = Column(Float, nullable=False)
    quality_score = Column(Float, default=90.0)
    on_time_delivery_rate = Column(Float, default=90.0)
    reliability_index = Column(Float, default=90.0)
    risk_score = Column(Float, default=25.0)
    capacity_monthly = Column(Integer, default=50000)
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class CustomerOrderDB(Base):
    __tablename__ = "customer_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, index=True, nullable=False)
    customer_name = Column(String(200), nullable=False)
    customer_tier = Column(String(100), default="Standard Commercial")
    contact_email = Column(String(200), nullable=False)
    sku_code = Column(String(100), default="SKU-MC-772")
    quantity = Column(Integer, default=1000)
    unit_price = Column(Float, default=145.0)
    order_value = Column(Float, default=145000.0)
    promised_eta = Column(String(50), nullable=False)
    revised_eta = Column(String(50), nullable=False)
    delay_days = Column(Integer, default=0)
    sla_penalty_exposure = Column(Float, default=0.0)
    status = Column(String(50), default="PENDING_ADVISORY")
    dispatched_at = Column(DateTime, nullable=True)

class NegotiationSessionDB(Base):
    __tablename__ = "negotiation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    supplier_code = Column(String(50), nullable=False)
    supplier_name = Column(String(200), nullable=False)
    sku_code = Column(String(100), nullable=False)
    current_round = Column(Integer, default=1)
    max_rounds = Column(Integer, default=10)
    status = Column(String(50), default="ACTIVE")
    buyer_target = Column(Float, nullable=False)
    supplier_target = Column(Float, nullable=False)
    current_offer = Column(Float, nullable=False)
    agreed_lead_time = Column(String(50), default="12 Days")
    agent_confidence = Column(Float, default=85.0)
    estimated_savings = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    bids = relationship("NegotiationBidDB", back_populates="session", cascade="all, delete-orphan")

class NegotiationBidDB(Base):
    __tablename__ = "negotiation_bids"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("negotiation_sessions.session_id"), nullable=False)
    round = Column(Integer, nullable=False)
    agent_id = Column(String(100), nullable=False)
    agent_name = Column(String(200), nullable=False)
    role = Column(String(50), nullable=False)
    proposed_price = Column(Float, nullable=False)
    proposed_lead_time_days = Column(Integer, default=12)
    proposed_sla_confidence = Column(Float, default=90.0)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="COUNTERED")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("NegotiationSessionDB", back_populates="bids")

class SimulationExperimentDB(Base):
    __tablename__ = "simulation_experiments"

    id = Column(Integer, primary_key=True, index=True)
    supplier_code = Column(String(50), nullable=False)
    scenario_tested = Column(String(200), nullable=False)
    monte_carlo_samples = Column(Integer, default=500)
    expected_cost_impact = Column(Float, nullable=False)
    cost_impact_p95 = Column(Float, nullable=False)
    stockout_probability = Column(Float, nullable=False)
    sla_breach_probability = Column(Float, nullable=False)
    expected_delay_days = Column(Float, nullable=False)
    risk_level = Column(String(50), default="MODERATE")
    quantiles_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class FulfillmentTelemetryDB(Base):
    __tablename__ = "fulfillment_telemetry"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(100), unique=True, index=True, nullable=False)
    unit_cost = Column(Float, nullable=False)
    quality_score = Column(Float, nullable=False)
    on_time_delivery_rate = Column(Float, nullable=False)
    reliability_index = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    predicted_lead_time_days = Column(Float, nullable=False)
    actual_lead_time_days = Column(Float, nullable=False)
    actual_optimal_decision = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CustomizationProfileDB(Base):
    __tablename__ = "customization_profiles"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(String(100), unique=True, index=True, default="default_enterprise")
    organization_name = Column(String(200), default="Rimberio Global Dynamics")
    config_json = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
