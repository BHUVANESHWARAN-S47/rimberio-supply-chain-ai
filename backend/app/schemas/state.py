from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from backend.app.schemas.buyer import BuyerRequirements, SupplierProposal, BuyerEvaluationResult

class SupplyChainState(BaseModel):
    """
    Unified multi-agent workflow state schema adhering to Section 12 specifications.
    Passed between agents during autonomous negotiation and counterfactual evaluation.
    """
    session_id: str
    user_query: Optional[str] = None
    buyer_requirements: Optional[BuyerRequirements] = None
    supplier_data: Optional[Dict[str, Any]] = None
    quotations: List[SupplierProposal] = Field(default_factory=list)
    buyer_evaluations: List[BuyerEvaluationResult] = Field(default_factory=list)
    negotiation_history: List[Dict[str, Any]] = Field(default_factory=list)
    price_analysis: Optional[Dict[str, Any]] = None
    risk_analysis: Optional[Dict[str, Any]] = None
    logistics_analysis: Optional[Dict[str, Any]] = None
    candidate_agreements: List[Dict[str, Any]] = Field(default_factory=list)
    cnt_results: Optional[Dict[str, Any]] = None
    supplier_comparison: Optional[Dict[str, Any]] = None
    customer_impact: Optional[Dict[str, Any]] = None
    decision: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
