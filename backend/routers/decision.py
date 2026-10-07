from fastapi import APIRouter
from backend.models.schemas import DecisionEvaluationRequest, DecisionOutcome
from backend.services.decision_engine import decision_engine

router = APIRouter(prefix="/api/decision", tags=["Adaptive Decision Module (Retain / Negotiate / Switch)"])

@router.post("/evaluate", response_model=DecisionOutcome)
def evaluate_adaptive_decision(req: DecisionEvaluationRequest):
    """
    Run MCDA evaluation and classify optimal enterprise policy:
    RETAIN, NEGOTIATE, or SWITCH.
    """
    return decision_engine.evaluate_decision(req)
