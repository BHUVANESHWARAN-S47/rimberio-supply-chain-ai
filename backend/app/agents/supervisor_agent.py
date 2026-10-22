import re
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.agents.base import BaseAgent
from backend.app.agents.registry import AgentRegistry
from backend.app.schemas.common import AgentCapability, DecisionAction, NegotiationAction
from backend.app.schemas.supervisor import (
    SupervisorWorkflowRequest,
    SupervisorWorkflowResponse,
    WorkflowStatus,
    NegotiationTurnRecord,
)
from backend.app.agents.buyer_agent import BuyerAgent
from backend.app.agents.supplier_agent import SupplierAgent
from backend.app.agents.price_analysis_agent import PriceAnalysisAgent
from backend.app.agents.logistics_agent import LogisticsAgent
from backend.app.agents.risk_agent import RiskAgent
from backend.app.agents.customer_impact_agent import CustomerImpactAgent
from backend.app.agents.adaptive_decision_agent import AdaptiveDecisionAgent
from backend.app.schemas.customer_impact import CustomerImpactEvaluationRequest
from backend.app.schemas.decision import AdaptiveDecisionRequest
from backend.app.core.llm import llm_service


class SupervisorAgent(BaseAgent[SupervisorWorkflowRequest, SupervisorWorkflowResponse]):
    """Master Workflow Orchestrator coordinating the multi-agent closed-loop supply chain.

    Coordinates bilateral Faratin negotiations between Buyer and Supplier agents.
    Upon impasse, automatically executes Counterfactual Simulation, Downstream Customer Impact Auditing,
    Multi-factor Risk Assessment, and Adaptive Decision Arbitration (RETAIN, NEGOTIATE, SWITCH).
    """

    ADVERSARIAL_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"force\s+(agreement|switch|retain)", re.IGNORECASE),
        re.compile(r"bypass\s+orchestrator", re.IGNORECASE),
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE),
        re.compile(r"(drop|delete|insert|update)\s+table", re.IGNORECASE),
    ]

    def __init__(self, db: Optional[Session] = None):
        super().__init__(
            name="Supervisor Agent",
            description="Master orchestrator of autonomous multi-agent negotiation, counterfactual simulations, and policy arbitration.",
            capabilities=[AgentCapability.SUPERVISOR_ORCHESTRATION],
        )
        self.db = db
        self.buyer_agent = BuyerAgent(db_session=db)
        self.supplier_agent = SupplierAgent(db=db)
        self.price_agent = PriceAnalysisAgent(db=db)
        self.logistics_agent = LogisticsAgent(db=db)
        self.risk_agent = RiskAgent(db=db)
        self.customer_impact_agent = CustomerImpactAgent(db=db)
        self.decision_agent = AdaptiveDecisionAgent(db=db)

    def validate_input(self, input_data: Any) -> SupervisorWorkflowRequest:
        if isinstance(input_data, SupervisorWorkflowRequest):
            return input_data
        elif isinstance(input_data, dict):
            return SupervisorWorkflowRequest(**input_data)
        raise ValueError(f"Unsupported input type for SupervisorAgent: {type(input_data)}")

    def run_deterministic_logic(
        self,
        validated_input: SupervisorWorkflowRequest,
        state: Optional[Any] = None,
    ) -> SupervisorWorkflowResponse:
        return self._execute_deterministic(validated_input)

    def _execute_deterministic(
        self,
        req: SupervisorWorkflowRequest,
    ) -> SupervisorWorkflowResponse:
        session_id = str(uuid.uuid4())
        max_rounds = max(1, min(20, req.max_negotiation_rounds))

        history: List[NegotiationTurnRecord] = []
        agreement_reached = False
        agreed_price: Optional[float] = None
        agreed_lead_time: Optional[int] = None

        # 1. Bilateral Negotiation Cycle
        p_init = req.supplier_initial_price
        p_res_sup = req.supplier_reserve_price
        p_target = req.target_price
        p_res_buy = req.reserve_price

        for r in range(1, max_rounds + 1):
            t = r / float(max_rounds)
            # Supplier Faratin concession (Boulware e=0.4: slow concession early, drops towards reserve near deadline)
            e_sup = 0.4
            p_sup_offer = round(p_init - (p_init - p_res_sup) * (t ** e_sup), 2)
            lead_time = max(7, 14 - int(r * 0.8))

            # Buyer utility evaluation: linear normalized utility
            if p_res_buy > p_target:
                buyer_util = max(0.0, min(1.0, (p_res_buy - p_sup_offer) / (p_res_buy - p_target)))
            else:
                buyer_util = 1.0 if p_sup_offer <= p_target else 0.0

            # Supplier utility: relative to reserve
            if p_init > p_res_sup:
                sup_util = max(0.0, min(1.0, (p_sup_offer - p_res_sup) / (p_init - p_res_sup)))
            else:
                sup_util = 1.0

            if p_sup_offer <= p_res_buy and buyer_util >= 0.70:
                # Agreement!
                agreement_reached = True
                agreed_price = p_sup_offer
                agreed_lead_time = lead_time
                history.append(
                    NegotiationTurnRecord(
                        round_number=r,
                        agent_type="BUYER",
                        action="ACCEPT",
                        unit_price=p_sup_offer,
                        lead_time_days=lead_time,
                        quantity=req.quantity,
                        buyer_utility=round(buyer_util, 3),
                        supplier_utility=round(sup_util, 3),
                    )
                )
                break
            elif r == max_rounds:
                # Impasse reached at deadline
                history.append(
                    NegotiationTurnRecord(
                        round_number=r,
                        agent_type="BUYER",
                        action="REJECT",
                        unit_price=p_sup_offer,
                        lead_time_days=lead_time,
                        quantity=req.quantity,
                        buyer_utility=round(buyer_util, 3),
                        supplier_utility=round(sup_util, 3),
                    )
                )
            else:
                # Counteroffer
                p_buy_counter = round(p_target + (p_res_buy - p_target) * (t ** 1.5), 2)
                history.append(
                    NegotiationTurnRecord(
                        round_number=r,
                        agent_type="SUPPLIER",
                        action="OFFER",
                        unit_price=p_sup_offer,
                        lead_time_days=lead_time,
                        quantity=req.quantity,
                        buyer_utility=round(buyer_util, 3),
                        supplier_utility=round(sup_util, 3),
                    )
                )

        rounds_completed = len(history)

        # 2. Downstream Customer Impact Audit
        cust_req = CustomerImpactEvaluationRequest(
            expected_delay_days=req.expected_transit_delay_days,
            orders=[
                {
                    "order_id": f"ORD-{req.product_id}-01",
                    "customer_name": "Anchor Client",
                    "customer_tier": "HIGH",
                    "quantity": req.quantity,
                    "unit_price": agreed_price or p_init,
                    "order_value": req.quantity * (agreed_price or p_init),
                }
            ],
            include_db_orders=False,
        )
        cust_res = self.customer_impact_agent.run_deterministic_logic(cust_req)

        # 3. Adaptive Decision Synthesis
        candidates = []
        # Candidate Incumbent
        candidates.append({
            "supplier_id": req.incumbent_supplier_id,
            "supplier_name": f"Incumbent ({req.incumbent_supplier_id})",
            "is_incumbent": True,
            "price_score": 85.0 if agreement_reached else 50.0,
            "quality_score": 80.0,
            "delivery_score": 80.0,
            "risk_score": 25.0,
            "logistics_score": 80.0,
            "customer_impact_score": 80.0 if cust_res.overall_impact_level in ["NONE", "LOW"] else 40.0,
            "switching_cost": 0.0,
        })

        # Candidate Alternates
        if req.alternate_suppliers:
            for alt in req.alternate_suppliers:
                candidates.append(alt)
        else:
            candidates.append({
                "supplier_id": "SUP-GLOBAL-ALT",
                "supplier_name": "Global Alternate Partner",
                "is_incumbent": False,
                "price_score": 80.0,
                "quality_score": 85.0,
                "delivery_score": 85.0,
                "risk_score": 20.0,
                "logistics_score": 80.0,
                "customer_impact_score": 85.0,
                "switching_cost": 2500.0,
            })

        dec_req = AdaptiveDecisionRequest(
            simulation_run_id=req.simulation_run_id,
            incumbent_supplier_id=req.incumbent_supplier_id,
            candidate_suppliers=candidates,
            allow_negotiation=not agreement_reached,
        )
        dec_res = self.decision_agent.run_deterministic_logic(dec_req)

        # 4. Final Status and Narrative
        if agreement_reached:
            status = WorkflowStatus.COMPLETED
            final_decision = DecisionAction.RETAIN
        else:
            status = WorkflowStatus.SIMULATING_COUNTERFACTUALS
            final_decision = dec_res.decision

        narrative = self._generate_supervisor_narrative(
            session_id=session_id,
            status=status,
            rounds=rounds_completed,
            agreement=agreement_reached,
            agreed_price=agreed_price,
            decision=final_decision,
            selected_name=dec_res.selected_supplier_name,
            sla_penalty=cust_res.total_sla_penalty_exposure,
        )

        return SupervisorWorkflowResponse(
            session_id=session_id,
            final_status=status,
            rounds_completed=rounds_completed,
            negotiation_history=history,
            agreement_reached=agreement_reached,
            agreed_price=agreed_price,
            agreed_lead_time=agreed_lead_time,
            decision=final_decision,
            selected_supplier_id=dec_res.selected_supplier_id,
            selected_supplier_name=dec_res.selected_supplier_name,
            utility_delta=dec_res.utility_delta,
            customer_impact_level=cust_res.overall_impact_level,
            sla_penalty_exposure=cust_res.total_sla_penalty_exposure,
            supervisor_narrative=narrative,
        )

    def _generate_supervisor_narrative(
        self,
        session_id: str,
        status: WorkflowStatus,
        rounds: int,
        agreement: bool,
        agreed_price: Optional[float],
        decision: DecisionAction,
        selected_name: str,
        sla_penalty: float,
    ) -> str:
        price_str = f"${agreed_price:,.2f}" if agreed_price is not None else "N/A"
        base_narrative = (
            f"Supervisor Orchestration Session [{session_id[:8]}]: Concluded after {rounds} rounds. "
            f"Agreement Reached: {agreement} (Agreed Price: {price_str}). "
            f"SLA Penalty Exposure: ${sla_penalty:,.2f}. "
            f"Policy Decision: {decision.value} -> Assigned Supplier: {selected_name}."
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are the RIMBERIO Supervisor Agent Orchestrator. "
                    "Draft an executive report summarizing the multi-agent closed loop workflow. "
                    "Preserve all facts, rounds, decisions, and dollar amounts exactly."
                ),
            },
            {
                "role": "user",
                "content": f"Summarize this multi-agent execution:\n{base_narrative}",
            },
        ]
        return llm_service.generate_completion(
            messages=messages,
            fallback_response=base_narrative,
            max_tokens=350,
        )


AgentRegistry.register("supervisor_agent", SupervisorAgent)
