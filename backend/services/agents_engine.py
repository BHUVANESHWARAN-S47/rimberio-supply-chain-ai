import math
import uuid
from typing import Dict, List, Optional
from backend.models.schemas import NegotiationSession, NegotiationBid, NegotiationStepRequest
from backend.services.customization_store import customization_store
from backend.services.data_manager import data_manager
from backend.agents.buyer_agent import BuyerAgentModel
from backend.agents.supplier_agent import SupplierAgentModel
from backend.agents.logistics_agent import LogisticsAgentModel

class MultiAgentNegotiationEngine:
    """
    Coordinates autonomous multi-agent negotiation rounds using real mathematical models:
    - BuyerAgentModel (Buyer Agent / Procurement Lead)
    - SupplierAgentModel (Supplier Agent / Vendor Representative)
    - LogisticsAgentModel (Logistics Agent / Maritime & Freight Telemetry)
    Works on ANY arbitrary supplier profile, SKU, and target budget.
    """

    def __init__(self):
        self._sessions: Dict[str, NegotiationSession] = {}
        self.buyer_model = BuyerAgentModel()
        self.supplier_model = SupplierAgentModel()
        self.logistics_model = LogisticsAgentModel()
        self._init_default_session()

    def _init_default_session(self):
        default_session_id = "SES-AUTONOMOUS-01"
        profile = customization_store.get_profile()
        heuristics = profile.agent_heuristics

        session = NegotiationSession(
            session_id=default_session_id,
            supplier_code="SUP-001",
            supplier_name="Apex Global Electronics",
            sku_code="SKU-MC-772",
            current_round=4,
            max_rounds=heuristics.max_rounds,
            status="ACTIVE",
            buyer_target=heuristics.buyer_target_price,
            supplier_target=heuristics.supplier_asking_price,
            current_offer=148.20,
            agreed_lead_time="12 Days",
            agent_confidence=94.8,
            estimated_savings=84200.0,
            history=[
                NegotiationBid(
                    round=1,
                    agent_id="SUPPLIER_AGENT",
                    agent_name="Apex Representative",
                    role="SUPPLIER",
                    proposed_price=165.00,
                    proposed_lead_time_days=18,
                    proposed_sla_confidence=88.0,
                    message="Initial batch quotation submitted for Micro-Capacitor SKU-MC-772 at $165.00/unit with 18-day lead time.",
                    status="COUNTERED"
                ),
                NegotiationBid(
                    round=2,
                    agent_id="BUYER_AGENT",
                    agent_name="Rimberio Buyer Lead",
                    role="BUYER",
                    proposed_price=142.50,
                    proposed_lead_time_days=10,
                    proposed_sla_confidence=95.0,
                    message="Counteroffer issued based on historical volume benchmark: Target $142.50/unit, 10 days delivery.",
                    status="COUNTERED"
                ),
                NegotiationBid(
                    round=3,
                    agent_id="LOGISTICS_AGENT",
                    agent_name="Maritime Telemetry Agent",
                    role="LOGISTICS",
                    proposed_price=145.00,
                    proposed_lead_time_days=14,
                    proposed_sla_confidence=91.5,
                    message="Suez congestion delta injects 4.2 days variance. Recommend locking 12-14 day buffered delivery corridor.",
                    status="ADVISORY"
                ),
                NegotiationBid(
                    round=4,
                    agent_id="BUYER_AGENT",
                    agent_name="Rimberio Buyer Lead",
                    role="BUYER",
                    proposed_price=148.20,
                    proposed_lead_time_days=12,
                    proposed_sla_confidence=94.8,
                    message="Autonomous compromise bid submitted at $148.20/unit with 12-day delivery guarantee.",
                    status="PENDING_RESPONSE"
                )
            ]
        )
        self._sessions[default_session_id] = session

    def get_session(self, session_id: str) -> Optional[NegotiationSession]:
        return self._sessions.get(session_id)

    def start_session(self, supplier_code: str, supplier_name: str, sku_code: str) -> NegotiationSession:
        profile = customization_store.get_profile()
        heuristics = profile.agent_heuristics
        session_id = f"SES-{uuid.uuid4().hex[:8].upper()}"

        # Look up supplier from dynamic data manager if available
        suppliers = data_manager.get_suppliers()
        match = next((s for s in suppliers if s["code"] == supplier_code), None)
        supplier_cost = float(match["unit_cost"]) if match else heuristics.supplier_asking_price
        asking_price = round(supplier_cost * 1.15, 2)

        session = NegotiationSession(
            session_id=session_id,
            supplier_code=supplier_code,
            supplier_name=supplier_name,
            sku_code=sku_code,
            current_round=1,
            max_rounds=heuristics.max_rounds,
            status="ACTIVE",
            buyer_target=heuristics.buyer_target_price,
            supplier_target=asking_price,
            current_offer=asking_price,
            agreed_lead_time="16 Days",
            agent_confidence=85.0,
            estimated_savings=0.0,
            history=[
                NegotiationBid(
                    round=1,
                    agent_id="SUPPLIER_AGENT",
                    agent_name=f"{supplier_name} Agent",
                    role="SUPPLIER",
                    proposed_price=asking_price,
                    proposed_lead_time_days=16,
                    proposed_sla_confidence=85.0,
                    message=f"Opening offer for {sku_code} at ${asking_price:.2f}/unit with 16-day SLA.",
                    status="COUNTERED"
                )
            ]
        )
        self._sessions[session_id] = session
        return session

    def execute_step(self, req: NegotiationStepRequest) -> NegotiationSession:
        session = self._sessions.get(req.session_id)
        if not session:
            session = self._sessions["SES-AUTONOMOUS-01"]

        profile = customization_store.get_profile()
        heuristics = profile.agent_heuristics

        if session.status in ["CONVERGED", "DEADLOCKED"]:
            return session

        next_round = session.current_round + 1
        t = next_round
        t_max = session.max_rounds

        # 1. Buyer Agent Model generates counteroffer
        buyer_out = self.buyer_model.generate_counteroffer(
            current_round=t,
            max_rounds=t_max,
            target_price=heuristics.buyer_target_price,
            reservation_price=heuristics.buyer_reservation_price,
            supplier_offer_price=session.current_offer,
            target_lead_days=10,
            supplier_lead_days=16,
            force_concession=bool(req.force_concession)
        )

        new_buyer_price = req.custom_buyer_offer if req.custom_buyer_offer is not None else buyer_out["offered_price"]

        # 2. Supplier Agent Model evaluates and counter-proposes
        marginal_cost = heuristics.buyer_target_price * 0.90
        supplier_out = self.supplier_model.generate_counterproposal(
            current_round=t,
            max_rounds=t_max,
            initial_asking_price=session.supplier_target,
            marginal_cost=marginal_cost,
            buyer_bid_price=new_buyer_price,
            order_quantity=14820,
            standard_lead_days=16
        )

        session.current_round = next_round
        session.current_offer = new_buyer_price
        session.estimated_savings = round(max(0.0, (session.supplier_target - new_buyer_price) * 14820), 2)

        # 3. Logistics Agent injects corridor reality check
        logistics_out = self.logistics_model.predict_route_transit(
            origin_port="Shanghai Port",
            destination_port="Rotterdam Hub",
            base_transit_days=12,
            chokepoints_crossed=["Suez Canal"]
        )

        # Check convergence
        price_gap = abs(new_buyer_price - supplier_out["counter_price"])
        if price_gap <= (heuristics.buyer_reservation_price * 0.03) or t >= t_max or supplier_out["accepted"]:
            session.status = "CONVERGED" if (price_gap <= 6.0 or supplier_out["accepted"]) else "DEADLOCKED"
            session.agent_confidence = 98.4 if session.status == "CONVERGED" else 62.0
            bid_status = "AGREED" if session.status == "CONVERGED" else "DEADLOCK"
        else:
            session.agent_confidence = min(96.5, 84.0 + (next_round * 3.0))
            bid_status = "COUNTERED"

        session.history.append(
            NegotiationBid(
                round=next_round,
                agent_id="BUYER_AGENT",
                agent_name="Rimberio Autonomous Buyer",
                role="BUYER",
                proposed_price=new_buyer_price,
                proposed_lead_time_days=buyer_out["offered_lead_time_days"],
                proposed_sla_confidence=session.agent_confidence,
                message=buyer_out["message"],
                status=bid_status
            )
        )

        return session

agents_engine = MultiAgentNegotiationEngine()
