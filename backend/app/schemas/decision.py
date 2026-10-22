from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from backend.app.schemas.common import DecisionAction


class SupplierCandidateEvaluation(BaseModel):
    supplier_id: str
    supplier_name: str
    is_incumbent: bool = False
    price_score: float = Field(ge=0.0, le=100.0)
    quality_score: float = Field(ge=0.0, le=100.0)
    delivery_score: float = Field(ge=0.0, le=100.0)
    reliability_score: float = Field(ge=0.0, le=100.0)
    risk_score: float = Field(ge=0.0, le=100.0)
    logistics_score: float = Field(ge=0.0, le=100.0)
    customer_impact_score: float = Field(ge=0.0, le=100.0)
    switching_cost: float = Field(default=0.0, ge=0.0)
    overall_utility: float = Field(ge=0.0, le=100.0)
    rank: int = Field(ge=1)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class AdaptiveDecisionRequest(BaseModel):
    simulation_run_id: Optional[str] = None
    incumbent_supplier_id: str
    candidate_suppliers: List[Dict[str, Any]]
    switching_threshold_utility_gain: float = Field(default=5.0, ge=0.0)
    max_acceptable_risk: float = Field(default=75.0, ge=0.0, le=100.0)
    weights: Optional[Dict[str, float]] = None
    allow_negotiation: bool = True
    context_notes: Optional[str] = None


class AdaptiveDecisionResponse(BaseModel):
    decision: DecisionAction
    selected_supplier_id: str
    selected_supplier_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    utility_delta: float
    net_financial_benefit: float
    supplier_rankings: List[SupplierCandidateEvaluation]
    key_tradeoffs: List[str]
    reasoning: str
    executive_summary: str
