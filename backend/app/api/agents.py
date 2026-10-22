from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from backend.app.database.connection import get_db
from backend.app.agents.registry import agent_registry, AgentRegistry
from backend.app.schemas.supervisor import (
    SupervisorWorkflowRequest,
    SupervisorWorkflowResponse,
)
from backend.app.schemas.decision import (
    AdaptiveDecisionRequest,
    AdaptiveDecisionResponse,
)
from backend.app.schemas.customer_impact import (
    CustomerImpactEvaluationRequest,
    CustomerImpactEvaluationResponse,
)
from backend.app.schemas.explanation import (
    ExplanationRequest,
    ExplanationResponse,
)
from backend.app.agents.supervisor_agent import SupervisorAgent
from backend.app.agents.adaptive_decision_agent import AdaptiveDecisionAgent
from backend.app.agents.customer_impact_agent import CustomerImpactAgent
from backend.app.agents.explanation_agent import ExplanationAgent

router = APIRouter(prefix="/api/agents", tags=["Multi-Agent Pipeline"])


@router.get("/registry", response_model=List[Dict[str, Any]])
def list_registered_agents():
    """Returns all autonomous agents registered in the RIMBERIO ecosystem."""
    return agent_registry.list_agents()


@router.post("/orchestrate", response_model=SupervisorWorkflowResponse)
def orchestrate_workflow(
    request: SupervisorWorkflowRequest,
    db: Session = Depends(get_db),
):
    """Executes closed-loop multi-agent negotiation, impasse handling, and simulation."""
    agent = SupervisorAgent(db=db)
    return agent.run_deterministic_logic(request)


@router.post("/decision", response_model=AdaptiveDecisionResponse)
def evaluate_policy_decision(
    request: AdaptiveDecisionRequest,
    db: Session = Depends(get_db),
):
    """Executes Multi-Criteria Decision Analysis to determine RETAIN, NEGOTIATE, or SWITCH."""
    agent = AdaptiveDecisionAgent(db=db)
    return agent.run_deterministic_logic(request)


@router.post("/customer-impact", response_model=CustomerImpactEvaluationResponse)
def evaluate_customer_impact(
    request: CustomerImpactEvaluationRequest,
    db: Session = Depends(get_db),
):
    """Audits downstream delivery delays, contractual SLA liabilities, and churn exposure."""
    agent = CustomerImpactAgent(db=db)
    return agent.run_deterministic_logic(request)


@router.post("/explain", response_model=ExplanationResponse)
def generate_explanation(
    request: ExplanationRequest,
    db: Session = Depends(get_db),
):
    """Synthesizes executive briefings and causal counterfactual rationales via Groq LLaMA."""
    agent = ExplanationAgent(db=db)
    return agent.run_deterministic_logic(request)
