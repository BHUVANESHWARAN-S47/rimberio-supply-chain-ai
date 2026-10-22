import re
import math
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.agents.base import BaseAgent
from backend.app.agents.registry import AgentRegistry
from backend.app.schemas.common import NegotiationAction, AgentCapability
from backend.app.schemas.supplier import (
    SupplierAgentInput, SupplierQuotationResult, SupplierProfile,
    BuyerOffer, ConcessionStrategy
)
from backend.app.database.connection import SessionLocal
from backend.app.database.models import SupplierDB, SupplierProductDB, ProductDB

class SupplierAgent(BaseAgent[SupplierAgentInput, SupplierQuotationResult]):
    """Supplier Representative AI Agent in RIMBERIO.
    Defends supplier margin floors, executes deterministic concession algorithms,
    enforces MOQs and lead time physics, and dynamically pulls parameters from PostgreSQL.
    """

    ADVERSARIAL_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"system\s+prompt\s+override", re.IGNORECASE),
        re.compile(r"set\s+price\s+to\s+0", re.IGNORECASE),
        re.compile(r"free\s+of\s+charge", re.IGNORECASE),
        re.compile(r"sell\s+at\s+zero\s+margin", re.IGNORECASE),
        re.compile(r"as\s+an\s+admin", re.IGNORECASE),
        re.compile(r"bypass\s+validation", re.IGNORECASE),
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE),
        re.compile(r"(drop|delete|insert|update)\s+table", re.IGNORECASE),
    ]

    def __init__(self, db: Optional[Session] = None):
        super().__init__(
            name="Supplier Agent",
            description="Autonomous supplier negotiator enforcing cost floors, concession curves, and MOQ constraints.",
            capabilities=[
                AgentCapability.PROPOSAL_EVALUATION,
                AgentCapability.CONCESSION_GENERATION,
                AgentCapability.COUNTEROFFER_FORMULATION
            ]
        )
        self.db = db

    def validate_input(self, input_data: Any) -> SupplierAgentInput:
        if isinstance(input_data, SupplierAgentInput):
            return input_data
        elif isinstance(input_data, dict):
            return SupplierAgentInput(**input_data)
        raise ValueError(f"Unsupported input type for SupplierAgent: {type(input_data)}")

    def run_deterministic_logic(
        self,
        validated_input: SupplierAgentInput,
        state: Optional[Any] = None
    ) -> SupplierQuotationResult:
        return self._execute_deterministic(validated_input)

    def _execute_deterministic(self, input_data: SupplierAgentInput) -> SupplierQuotationResult:
        # 1. Adversarial Inspection
        adversarial_flags = self._detect_adversarial_patterns(input_data.buyer_offer.buyer_notes)

        # 2. Resolve Supplier Profile (from input override or database)
        profile = self._resolve_profile(input_data)

        # 3. Compute Concession Parameters (Faratin Time-Dependent Curve)
        t = input_data.negotiation_round
        t_max = max(input_data.max_rounds, t)
        
        # Concession beta: Boulware (>1), Conceder (<1), Linear (=1)
        beta = profile.strategy_beta
        if profile.concession_strategy == ConcessionStrategy.LINEAR:
            beta = 1.0
        elif profile.concession_strategy == ConcessionStrategy.CONCEDER:
            beta = 0.5
        elif profile.concession_strategy == ConcessionStrategy.BOULWARE:
            beta = max(1.5, profile.strategy_beta)

        if t_max <= 1:
            alpha = 1.0
        else:
            alpha = math.pow((t - 1) / (t_max - 1), beta)
            alpha = max(0.0, min(1.0, alpha))

        # Target Price vs Reservation Price
        p_max = profile.target_price
        p_min = profile.reservation_price
        target_round_price = round(p_max - alpha * (p_max - p_min), 2)

        # Lead time concession
        l_base = profile.baseline_lead_time_days
        l_min = profile.min_lead_time_days
        target_round_lead_time = max(l_min, int(round(l_base - alpha * (l_base - l_min))))

        # 4. Evaluate Buyer Offer Against Supplier Physics
        offer = input_data.buyer_offer
        violations: List[str] = []

        # Check Price Floor
        price_too_low = offer.offered_unit_price < p_min
        if price_too_low:
            violations.append(f"Offered unit price (${offer.offered_unit_price:.2f}) breaches supplier reservation floor (${p_min:.2f}).")

        # Check MOQ
        qty_sub_moq = offer.quantity_demanded < profile.min_order_quantity
        if qty_sub_moq:
            violations.append(f"Demanded quantity ({offer.quantity_demanded}) is below MOQ ({profile.min_order_quantity}).")

        # Check Capacity
        qty_over_cap = offer.quantity_demanded > profile.max_capacity
        if qty_over_cap:
            violations.append(f"Demanded quantity ({offer.quantity_demanded}) exceeds maximum monthly capacity ({profile.max_capacity}).")

        # Check Lead Time
        delivery_too_fast = offer.requested_delivery_days < l_min
        if delivery_too_fast:
            violations.append(f"Requested delivery ({offer.requested_delivery_days} days) is shorter than minimum physical lead time ({l_min} days).")

        # Check Payment Terms
        terms_unacceptable = offer.payment_terms not in profile.acceptable_payment_terms
        if terms_unacceptable:
            violations.append(f"Requested payment terms '{offer.payment_terms}' are not approved. Acceptable: {profile.acceptable_payment_terms}.")

        # 5. Determine Supplier Action
        # Case A: Buyer offer satisfies target concession price AND has no hard constraint violations
        if offer.offered_unit_price >= target_round_price and not violations:
            action = NegotiationAction.ACCEPT
            quoted_price = offer.offered_unit_price
            quoted_qty = offer.quantity_demanded
            quoted_lead = offer.requested_delivery_days
            quoted_terms = offer.payment_terms
            reasoning = f"Buyer offer meets target round price (${target_round_price:.2f}) with acceptable terms. Agreement accepted in round {t}."

        # Case B: Final round & buyer offers at least reservation floor with no capacity violation
        elif t >= t_max and offer.offered_unit_price >= p_min and not qty_over_cap:
            action = NegotiationAction.ACCEPT
            quoted_price = max(offer.offered_unit_price, p_min)
            quoted_qty = max(offer.quantity_demanded, profile.min_order_quantity)
            quoted_lead = max(offer.requested_delivery_days, l_min)
            quoted_terms = offer.payment_terms if not terms_unacceptable else profile.acceptable_payment_terms[0]
            reasoning = f"Deadline round reached. Supplier clinches transaction at reservation threshold (${quoted_price:.2f})."

        # Case C: Severely predatory offer (< 60% of reservation floor) or deadlocked on final round
        elif (offer.offered_unit_price < p_min * 0.60) or (t >= t_max and price_too_low):
            action = NegotiationAction.REJECT
            quoted_price = target_round_price
            quoted_qty = max(offer.quantity_demanded, profile.min_order_quantity)
            quoted_lead = target_round_lead_time
            quoted_terms = profile.acceptable_payment_terms[0]
            reasoning = f"Offer severely unviable (${offer.offered_unit_price:.2f} vs floor ${p_min:.2f}). Supplier terminates bargaining."

        # Case D: Standard Counteroffer via Concession Curve
        else:
            action = NegotiationAction.COUNTEROFFER
            # Price concession logic: cannot go below p_min
            quoted_price = max(target_round_price, p_min)
            # Quantity: enforce MOQ and capacity
            quoted_qty = max(profile.min_order_quantity, min(offer.quantity_demanded, profile.max_capacity))
            # Lead time: clamp to physical minimum if buyer requests expedited delivery
            quoted_lead = l_min if delivery_too_fast else max(target_round_lead_time, l_min)
            # Terms: fallback to best acceptable term
            quoted_terms = offer.payment_terms if not terms_unacceptable else profile.acceptable_payment_terms[0]
            reasoning = (
                f"Round {t}/{t_max} counterproposal formulated via {profile.concession_strategy.value} concession strategy "
                f"(concession factor alpha={alpha:.2f}). Demanding ${quoted_price:.2f}/unit with {quoted_lead} days lead time."
            )

        # Margin calculation
        margin_pct = round((quoted_price - profile.cogs) / profile.cogs, 4)

        return SupplierQuotationResult(
            supplier_id=profile.supplier_id,
            supplier_code=profile.supplier_code,
            company_name=profile.company_name,
            product_id=profile.product_id,
            action=action,
            quoted_unit_price=quoted_price,
            quoted_quantity=quoted_qty,
            quoted_delivery_days=quoted_lead,
            quoted_payment_terms=quoted_terms,
            margin_pct=margin_pct,
            reservation_price=p_min,
            target_price=p_max,
            concession_rate=round(alpha, 4),
            constraint_violations=violations,
            reasoning=reasoning,
            adversarial_flags=adversarial_flags
        )

    def _resolve_profile(self, input_data: SupplierAgentInput) -> SupplierProfile:
        """Resolves supplier profile either from explicit input or from PostgreSQL."""
        if input_data.profile_override is not None:
            return input_data.profile_override

        # Attempt to load from PostgreSQL
        db = self.db or SessionLocal()
        try:
            # Query supplier
            supplier = db.query(SupplierDB).filter(
                (SupplierDB.id == input_data.supplier_id) | (SupplierDB.supplier_code == input_data.supplier_id)
            ).first()

            if supplier:
                # Query linked supplier product
                sp = db.query(SupplierProductDB).filter(
                    SupplierProductDB.supplier_id == supplier.id,
                    SupplierProductDB.product_id == input_data.product_id
                ).first()

                if sp:
                    cogs = round(sp.unit_price * 0.75, 2)
                    return SupplierProfile(
                        supplier_id=str(supplier.id),
                        supplier_code=supplier.supplier_code,
                        company_name=supplier.company_name,
                        product_id=input_data.product_id,
                        cogs=cogs,
                        min_margin_pct=0.15,
                        target_margin_pct=0.35,
                        min_order_quantity=sp.minimum_order_quantity,
                        max_capacity=sp.capacity,
                        baseline_lead_time_days=sp.lead_time_days,
                        min_lead_time_days=max(5, int(sp.lead_time_days * 0.6)),
                        acceptable_payment_terms=[supplier.payment_terms, "Net 30"] if supplier.payment_terms != "Net 30" else ["Net 30", "Net 45"]
                    )
        except Exception:
            pass
        finally:
            if not self.db:
                db.close()

        # Deterministic Fallback if not found in DB
        default_cogs = 100.0
        return SupplierProfile(
            supplier_id=input_data.supplier_id,
            supplier_code=input_data.supplier_id,
            company_name=f"Enterprise Supplier {input_data.supplier_id}",
            product_id=input_data.product_id,
            cogs=default_cogs,
            min_margin_pct=0.15,
            target_margin_pct=0.35,
            min_order_quantity=100,
            max_capacity=50000,
            baseline_lead_time_days=14,
            min_lead_time_days=7,
            acceptable_payment_terms=["Net 30", "Net 45"]
        )

    def _detect_adversarial_patterns(self, text: Optional[str]) -> List[str]:
        if not text:
            return []
        flags = []
        for pat in self.ADVERSARIAL_PATTERNS:
            if pat.search(text):
                flags.append(f"Prompt injection pattern detected: '{pat.pattern}'")
        return flags

# Register agent in AgentRegistry
AgentRegistry.register(
    name="Supplier Agent",
    agent_class=SupplierAgent,
    capabilities=[
        AgentCapability.PROPOSAL_EVALUATION,
        AgentCapability.CONCESSION_GENERATION,
        AgentCapability.COUNTEROFFER_FORMULATION
    ],
    version="1.0.0"
)
