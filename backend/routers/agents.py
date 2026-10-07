from fastapi import APIRouter, HTTPException
from backend.models.schemas import NegotiationSession, NegotiationStepRequest
from backend.services.agents_engine import agents_engine

router = APIRouter(prefix="/api/agents", tags=["Multi-Agent Autonomous Negotiation"])

@router.get("/negotiate/session/{session_id}", response_model=NegotiationSession)
def get_session(session_id: str):
    """Fetch current state and transcript of a negotiation session."""
    session = agents_engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Negotiation session not found")
    return session

@router.post("/negotiate/step", response_model=NegotiationSession)
def execute_negotiation_step(req: NegotiationStepRequest):
    """Execute the next autonomous bid/counteroffer in the negotiation."""
    return agents_engine.execute_step(req)

@router.post("/negotiate/start", response_model=NegotiationSession)
def start_negotiation_session(supplier_code: str = "SUP-001", supplier_name: str = "Apex Global Electronics", sku_code: str = "SKU-MC-772"):
    """Initialize a new autonomous multi-agent negotiation session."""
    return agents_engine.start_session(supplier_code, supplier_name, sku_code)
