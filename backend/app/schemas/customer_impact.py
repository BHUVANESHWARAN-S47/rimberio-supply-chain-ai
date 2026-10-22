import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class CustomerPriorityTier(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    STANDARD = "STANDARD"


class CustomerImpactLevel(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CustomerOrderImpact(BaseModel):
    order_id: str
    customer_id: str
    customer_name: str
    customer_tier: str = "STANDARD"
    product_id: str
    quantity: int = Field(ge=0)
    order_value: float = Field(ge=0.0)
    promised_delivery_date: str
    revised_delivery_date: str
    delay_days: int = Field(ge=0)
    daily_penalty_rate: float = Field(ge=0.0)
    sla_penalty_exposure: float = Field(ge=0.0)
    churn_risk_score: float = Field(ge=0.0, le=100.0)
    status: str = "PENDING_ADVISORY"


class CustomerNotificationPayload(BaseModel):
    customer_id: str
    customer_name: str
    notification_type: str = "SWITCHING_ADVISORY"
    title: str
    message: str
    severity: str = "INFO"  # INFO, WARNING, URGENT


class CustomerImpactEvaluationRequest(BaseModel):
    simulation_run_id: Optional[str] = None
    supplier_id: Optional[str] = None
    product_id: Optional[str] = None
    expected_delay_days: int = Field(default=0, ge=0)
    fill_rate_reduction: float = Field(default=0.0, ge=0.0, le=1.0)
    orders: Optional[List[Dict[str, Any]]] = None
    include_db_orders: bool = True


class CustomerImpactEvaluationResponse(BaseModel):
    total_orders_audited: int
    total_affected_units: int
    total_revenue_at_risk: float
    total_sla_penalty_exposure: float
    overall_impact_level: str
    critical_orders_count: int
    high_orders_count: int
    impacted_orders: List[CustomerOrderImpact]
    generated_notifications: List[CustomerNotificationPayload]
    executive_summary: str
