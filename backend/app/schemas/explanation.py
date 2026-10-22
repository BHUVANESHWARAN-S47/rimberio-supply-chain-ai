from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ExplanationMode(str, Enum):
    EXECUTIVE_DEBRIEF = "EXECUTIVE_DEBRIEF"
    CAUSAL_COUNTERFACTUAL = "CAUSAL_COUNTERFACTUAL"
    SUPPLIER_COMPARISON = "SUPPLIER_COMPARISON"
    INTERACTIVE_CHAT = "INTERACTIVE_CHAT"
    RISK_DEEPDIVE = "RISK_DEEPDIVE"


class ExplanationRequest(BaseModel):
    mode: ExplanationMode = ExplanationMode.EXECUTIVE_DEBRIEF
    user_query: Optional[str] = None
    decision_context: Optional[Dict[str, Any]] = None
    counterfactual_context: Optional[Dict[str, Any]] = None
    customer_impact_context: Optional[Dict[str, Any]] = None
    risk_context: Optional[Dict[str, Any]] = None
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    model_name: Optional[str] = None


class ExplanationResponse(BaseModel):
    title: str
    summary: str
    causal_reasoning_points: List[str]
    key_metrics_referenced: Dict[str, Any]
    tradeoff_analysis: str
    actionable_recommendations: List[str]
    full_narrative: str
    model_used: str
