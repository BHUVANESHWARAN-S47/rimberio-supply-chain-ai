from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from backend.app.schemas.common import DecisionAction, NegotiationAction


class WorkflowStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    NEGOTIATING = "NEGOTIATING"
    IMPASSE_TRIGGERED = "IMPASSE_TRIGGERED"
    SIMULATING_COUNTERFACTUALS = "SIMULATING_COUNTERFACTUALS"
    DECISION_FINALIZED = "DECISION_FINALIZED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class NegotiationTurnRecord(BaseModel):
    round_number: int
    agent_type: str  # "BUYER" or "SUPPLIER"
    action: str  # "OFFER", "COUNTEROFFER", "ACCEPT", "REJECT"
    unit_price: float
    lead_time_days: int
    quantity: int
    buyer_utility: float
    supplier_utility: float


class SupervisorWorkflowRequest(BaseModel):
    simulation_run_id: Optional[str] = None
    product_id: str = "PROD-DEFAULT"
    quantity: int = Field(default=1000, ge=1)
    incumbent_supplier_id: str
    target_price: float = Field(default=100.0, ge=0.0)
    reserve_price: float = Field(default=130.0, ge=0.0)
    supplier_initial_price: float = Field(default=140.0, ge=0.0)
    supplier_reserve_price: float = Field(default=110.0, ge=0.0)
    max_negotiation_rounds: int = Field(default=5, ge=1, le=20)
    alternate_suppliers: Optional[List[Dict[str, Any]]] = None
    expected_transit_delay_days: int = Field(default=0, ge=0)
    context_notes: Optional[str] = None


class SupervisorWorkflowResponse(BaseModel):
    session_id: str
    final_status: WorkflowStatus
    rounds_completed: int
    negotiation_history: List[NegotiationTurnRecord]
    agreement_reached: bool
    agreed_price: Optional[float] = None
    agreed_lead_time: Optional[int] = None
    decision: DecisionAction
    selected_supplier_id: str
    selected_supplier_name: str
    utility_delta: float
    customer_impact_level: str
    sla_penalty_exposure: float
    supervisor_narrative: str
