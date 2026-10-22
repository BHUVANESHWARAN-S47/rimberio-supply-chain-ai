import re
import math
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field

from backend.app.agents.base import BaseAgent
from backend.app.schemas.common import AgentCapability, NegotiationAction
from backend.app.schemas.buyer import (
    BuyerRequirements,
    SupplierProposal,
    BuyerConstraintViolation,
    BuyerEvaluationResult,
)
from backend.app.schemas.state import SupplyChainState

# Common adversarial & injection patterns in B2B supplier proposals
ADVERSARIAL_INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"system prompt",
    r"you are now (an? )?admin",
    r"override (decision|price|constraint)",
    r"recommend(ation)?\s*:\s*accept",
    r"drop table",
    r"<script.*?>",
    r"set (utility|score) to 1",
    r"bypass (validation|rule)",
]

class BuyerEvaluationInput(BaseModel):
    requirements: BuyerRequirements
    proposal: SupplierProposal

class BuyerAgent(BaseAgent[BuyerEvaluationInput, BuyerEvaluationResult]):
    """
    Autonomous Enterprise Buyer Agent.
    Represents the procurement organization, rigorously enforces hard constraints,
    calculates multi-attribute utility, detects prompt injections, and generates
    grounded counteroffers without relying on LLM hallucinations for math.
    """
    
    def __init__(
        self,
        db_session: Optional[Any] = None,
        llm_client: Optional[Any] = None
    ):
        super().__init__(
            name="BuyerAgent",
            description="Evaluates vendor quotations against enterprise constraints, computes deterministic MAUT utility, and formulates counteroffers.",
            capabilities=[
                AgentCapability.REQUIREMENT_EXTRACTION,
                AgentCapability.PROPOSAL_EVALUATION,
                AgentCapability.UTILITY_SCORING,
                AgentCapability.COUNTEROFFER_GENERATION,
            ],
            db_session=db_session,
            llm_client=llm_client
        )

    def validate_input(self, input_data: Any) -> BuyerEvaluationInput:
        if isinstance(input_data, BuyerEvaluationInput):
            return input_data
        if isinstance(input_data, dict):
            req_data = input_data.get("requirements", {})
            prop_data = input_data.get("proposal", {})
            return BuyerEvaluationInput(
                requirements=BuyerRequirements(**req_data),
                proposal=SupplierProposal(**prop_data)
            )
        raise ValueError(f"Invalid input type for BuyerAgent: {type(input_data)}")

    def sanitize_and_check_security(self, notes: Optional[str]) -> Tuple[Optional[str], bool, Optional[str]]:
        """Detect prompt injection and malicious attempts in vendor notes."""
        if not notes:
            return None, False, None
            
        text_lower = notes.lower()
        for pattern in ADVERSARIAL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                sanitized = re.sub(pattern, "[FLAGGED_CONTENT_REMOVED]", notes, flags=re.IGNORECASE)
                return sanitized, True, f"Detected adversarial injection attempt matching pattern: {pattern}"
                
        # Clean basic HTML/script tags
        sanitized = re.sub(r"<[^>]*>", "", notes)
        return sanitized, False, None

    def evaluate_constraints(
        self, req: BuyerRequirements, prop: SupplierProposal
    ) -> Tuple[List[BuyerConstraintViolation], List[BuyerConstraintViolation]]:
        """
        Deterministic constraint checker.
        Classifies hard vs soft constraint violations.
        """
        hard_violations: List[BuyerConstraintViolation] = []
        soft_violations: List[BuyerConstraintViolation] = []

        # 1. Price Hard Constraint
        if prop.proposed_unit_price > req.max_price:
            hard_violations.append(BuyerConstraintViolation(
                constraint_type="PRICE",
                expected=f"<= ${req.max_price:.2f}",
                actual=f"${prop.proposed_unit_price:.2f}",
                severity="HARD",
                message=f"Proposed price ${prop.proposed_unit_price:.2f} exceeds ceiling price of ${req.max_price:.2f}"
            ))
        elif req.target_price and prop.proposed_unit_price > req.target_price:
            soft_violations.append(BuyerConstraintViolation(
                constraint_type="PRICE",
                expected=f"<= ${req.target_price:.2f}",
                actual=f"${prop.proposed_unit_price:.2f}",
                severity="SOFT",
                message=f"Proposed price ${prop.proposed_unit_price:.2f} is above preferred target price of ${req.target_price:.2f}"
            ))

        # 2. Quality Hard Constraint
        if prop.proposed_quality_score < req.min_quality:
            hard_violations.append(BuyerConstraintViolation(
                constraint_type="QUALITY",
                expected=f">= {req.min_quality:.1f}",
                actual=f"{prop.proposed_quality_score:.1f}",
                severity="HARD",
                message=f"Proposed quality {prop.proposed_quality_score:.1f} is below mandatory threshold of {req.min_quality:.1f}"
            ))

        # 3. Delivery Lead Time Hard Constraint
        if prop.proposed_delivery_days > req.max_delivery_days:
            hard_violations.append(BuyerConstraintViolation(
                constraint_type="DELIVERY",
                expected=f"<= {req.max_delivery_days} days",
                actual=f"{prop.proposed_delivery_days} days",
                severity="HARD",
                message=f"Lead time {prop.proposed_delivery_days} days exceeds delivery deadline of {req.max_delivery_days} days"
            ))
        elif req.target_delivery_days and prop.proposed_delivery_days > req.target_delivery_days:
            soft_violations.append(BuyerConstraintViolation(
                constraint_type="DELIVERY",
                expected=f"<= {req.target_delivery_days} days",
                actual=f"{prop.proposed_delivery_days} days",
                severity="SOFT",
                message=f"Lead time {prop.proposed_delivery_days} days exceeds target lead time of {req.target_delivery_days} days"
            ))

        # 4. Reliability Index Constraint
        if prop.reliability_index < req.min_reliability:
            hard_violations.append(BuyerConstraintViolation(
                constraint_type="RELIABILITY",
                expected=f">= {req.min_reliability:.1f}",
                actual=f"{prop.reliability_index:.1f}",
                severity="HARD",
                message=f"Reliability index {prop.reliability_index:.1f} falls below required minimum of {req.min_reliability:.1f}"
            ))

        # 5. Geopolitical / Route Risk Constraint
        if prop.risk_score > req.max_risk_score:
            hard_violations.append(BuyerConstraintViolation(
                constraint_type="RISK",
                expected=f"<= {req.max_risk_score:.1f}",
                actual=f"{prop.risk_score:.1f}",
                severity="HARD",
                message=f"Risk score {prop.risk_score:.1f} exceeds allowable risk tolerance of {req.max_risk_score:.1f}"
            ))

        # 6. Payment Terms Constraint
        if req.acceptable_payment_terms and prop.payment_terms not in req.acceptable_payment_terms:
            hard_violations.append(BuyerConstraintViolation(
                constraint_type="PAYMENT_TERMS",
                expected=f"One of {req.acceptable_payment_terms}",
                actual=prop.payment_terms,
                severity="HARD",
                message=f"Payment terms '{prop.payment_terms}' not accepted by enterprise policy"
            ))

        # 7. Quantity Constraint
        if prop.proposed_quantity < req.quantity:
            hard_violations.append(BuyerConstraintViolation(
                constraint_type="QUANTITY",
                expected=f">= {req.quantity}",
                actual=f"{prop.proposed_quantity}",
                severity="HARD",
                message=f"Supplier capacity {prop.proposed_quantity} cannot meet required order volume of {req.quantity}"
            ))

        return hard_violations, soft_violations

    def calculate_utilities(
        self, req: BuyerRequirements, prop: SupplierProposal
    ) -> Tuple[float, float, float, float, float, float]:
        """
        Calculates normalized dimension utilities and overall Multi-Attribute Utility (MAUT).
        All calculations are bounded in [0.0, 1.0].
        """
        # 1. Price Utility: Lower price is better
        target_p = req.target_price if req.target_price else req.max_price * 0.85
        if prop.proposed_unit_price <= target_p:
            u_price = 1.0
        elif prop.proposed_unit_price >= req.max_price:
            u_price = 0.0
        else:
            u_price = (req.max_price - prop.proposed_unit_price) / (req.max_price - target_p)
        u_price = max(0.0, min(1.0, u_price))

        # 2. Quality Utility: Higher quality is better
        if prop.proposed_quality_score >= 100.0:
            u_quality = 1.0
        elif prop.proposed_quality_score <= req.min_quality:
            u_quality = 0.0
        else:
            denom = 100.0 - req.min_quality
            u_quality = (prop.proposed_quality_score - req.min_quality) / (denom if denom > 0 else 1.0)
        u_quality = max(0.0, min(1.0, u_quality))

        # 3. Delivery Utility: Shorter lead time is better
        target_d = req.target_delivery_days if req.target_delivery_days else max(1, int(req.max_delivery_days * 0.7))
        if prop.proposed_delivery_days <= target_d:
            u_delivery = 1.0
        elif prop.proposed_delivery_days >= req.max_delivery_days:
            u_delivery = 0.0
        else:
            denom = req.max_delivery_days - target_d
            u_delivery = (req.max_delivery_days - prop.proposed_delivery_days) / (denom if denom > 0 else 1.0)
        u_delivery = max(0.0, min(1.0, u_delivery))

        # 4. Reliability Utility: Higher reliability is better
        if prop.reliability_index >= 100.0:
            u_reliability = 1.0
        elif prop.reliability_index <= req.min_reliability:
            u_reliability = 0.0
        else:
            denom = 100.0 - req.min_reliability
            u_reliability = (prop.reliability_index - req.min_reliability) / (denom if denom > 0 else 1.0)
        u_reliability = max(0.0, min(1.0, u_reliability))

        # 5. Risk Utility: Lower risk is better
        if prop.risk_score <= 0.0:
            u_risk = 1.0
        elif prop.risk_score >= req.max_risk_score:
            u_risk = 0.0
        else:
            u_risk = (req.max_risk_score - prop.risk_score) / (req.max_risk_score if req.max_risk_score > 0 else 1.0)
        u_risk = max(0.0, min(1.0, u_risk))

        # Overall Weighted MAUT
        w = req.weights
        overall = (
            w.cost * u_price +
            w.quality * u_quality +
            w.delivery * u_delivery +
            w.reliability * u_reliability +
            w.risk * u_risk
        )
        overall = max(0.0, min(1.0, overall))

        return overall, u_price, u_quality, u_delivery, u_reliability, u_risk

    def formulate_counteroffer(
        self, req: BuyerRequirements, prop: SupplierProposal
    ) -> Tuple[float, int, int]:
        """
        Deterministically formulates counter-proposals within procurement bounds.
        """
        # Price Counteroffer
        target_p = req.target_price if req.target_price else req.max_price * 0.90
        # Offer midpoint between target and proposed price, capped strictly at max_price
        counter_p = min(req.max_price, round((prop.proposed_unit_price + target_p) / 2.0, 2))
        if counter_p > req.max_price:
            counter_p = req.max_price

        # Delivery Counteroffer
        target_d = req.target_delivery_days if req.target_delivery_days else max(1, int(req.max_delivery_days * 0.8))
        counter_d = min(req.max_delivery_days, int(math.ceil((prop.proposed_delivery_days + target_d) / 2.0)))
        
        # Quantity Counteroffer
        counter_q = max(req.quantity, prop.proposed_quantity)

        return counter_p, counter_d, counter_q

    def run_deterministic_logic(
        self, validated_input: BuyerEvaluationInput, state: Optional[SupplyChainState] = None
    ) -> BuyerEvaluationResult:
        req = validated_input.requirements
        prop = validated_input.proposal

        # 1. Security & Sanitization
        sanitized_notes, sec_flagged, sec_reason = self.sanitize_and_check_security(prop.notes)

        # 2. Evaluate Hard and Soft Constraints
        hard_violations, soft_violations = self.evaluate_constraints(req, prop)

        # 3. Calculate Utilities
        overall_u, u_p, u_q, u_d, u_r, u_k = self.calculate_utilities(req, prop)

        # 4. Recommendation Decision Logic
        # Rule A: If security injection attempt detected, reject or flag with strict refusal
        if sec_flagged:
            recommendation = NegotiationAction.REJECT
            explanation = f"Quotation rejected due to security violation: {sec_reason}"
            return BuyerEvaluationResult(
                supplier_id=prop.supplier_id,
                recommendation=recommendation,
                overall_utility=0.0,
                hard_constraint_violations=hard_violations,
                soft_constraint_violations=soft_violations,
                is_valid=False,
                price_utility=0.0,
                quality_utility=0.0,
                delivery_utility=0.0,
                reliability_utility=0.0,
                risk_utility=0.0,
                explanation=explanation,
                sanitized_notes=sanitized_notes,
                security_flagged=True,
                security_reason=sec_reason
            )

        # Rule B: Hard constraint breaches
        if len(hard_violations) > 0:
            # Check if violations are strictly non-negotiable or beyond counteroffer margins
            # Price beyond acceptable counter margin
            counter_margin = 1.0 + (req.counteroffer_margin_percent / 100.0)
            severe_price_breach = prop.proposed_unit_price > (req.max_price * counter_margin)
            severe_quality_breach = prop.proposed_quality_score < (req.min_quality - 10.0)
            severe_risk_breach = prop.risk_score > (req.max_risk_score + 15.0)

            if severe_price_breach or severe_quality_breach or severe_risk_breach or len(hard_violations) >= 3:
                recommendation = NegotiationAction.REJECT
                explanation = f"Proposal rejected due to severe hard constraint violations: {', '.join([v.message for v in hard_violations])}"
                counter_p, counter_d, counter_q = None, None, None
            else:
                # Moderate breach: Issue strict counteroffer asserting buyer hard limits
                recommendation = NegotiationAction.COUNTEROFFER
                counter_p, counter_d, counter_q = self.formulate_counteroffer(req, prop)
                explanation = f"Proposal violates constraints ({', '.join([v.constraint_type for v in hard_violations])}). Issuing counteroffer at buyer ceiling terms."
        else:
            # All hard constraints met!
            if overall_u >= req.minimum_utility_threshold and len(soft_violations) == 0:
                recommendation = NegotiationAction.ACCEPT
                counter_p, counter_d, counter_q = None, None, None
                explanation = f"Proposal accepted with favorable multi-attribute utility score of {overall_u:.3f} (threshold: {req.minimum_utility_threshold:.2f})."
            else:
                recommendation = NegotiationAction.COUNTEROFFER
                counter_p, counter_d, counter_q = self.formulate_counteroffer(req, prop)
                reasons = [v.message for v in soft_violations] or [f"Utility {overall_u:.3f} below acceptance threshold {req.minimum_utility_threshold:.2f}"]
                explanation = f"Issuing counteroffer to optimize procurement utility: {'; '.join(reasons)}"

        return BuyerEvaluationResult(
            supplier_id=prop.supplier_id,
            recommendation=recommendation,
            overall_utility=round(overall_u, 4),
            hard_constraint_violations=hard_violations,
            soft_constraint_violations=soft_violations,
            is_valid=True,
            price_utility=round(u_p, 4),
            quality_utility=round(u_q, 4),
            delivery_utility=round(u_d, 4),
            reliability_utility=round(u_r, 4),
            risk_utility=round(u_k, 4),
            counteroffer_price=counter_p,
            counteroffer_delivery_days=counter_d,
            counteroffer_quantity=counter_q,
            explanation=explanation,
            sanitized_notes=sanitized_notes,
            security_flagged=False
        )

    def extract_requirements_from_text(self, natural_language_text: str) -> BuyerRequirements:
        """
        LLM / Regex Dual-Layer Interpretation Layer:
        Parses unstructured natural language procurement memos into typed BuyerRequirements.
        Never hallucinates numbers when text contains explicit constraints.
        """
        text = natural_language_text
        
        # 1. Regex Extraction Baseline
        qty_match = re.search(r"(\d[\d,]*)\s*(units|pcs|pieces|items|quantity|qty)", text, re.I)
        qty = int(qty_match.group(1).replace(",", "")) if qty_match else 1000

        price_match = re.search(r"(?:max(?:imum)?\s*price|ceiling|budget|under|below|\$)\s*(\$?\d+(?:\.\d+)?)", text, re.I)
        if not price_match:
            price_match = re.search(r"\$\s*(\d+(?:\.\d+)?)", text)
        max_p = float(price_match.group(1).replace("$", "")) if price_match else 150.0

        delivery_match = re.search(r"(\d+)\s*(days?|business days?|weeks?)", text, re.I)
        if delivery_match:
            val = int(delivery_match.group(1))
            days = val * 7 if "week" in delivery_match.group(2).lower() else val
        else:
            days = 14

        quality_match = re.search(r"(?:quality|grade)\s*(?:of|at least|>=|min(?:imum)?)?\s*(\d+(?:\.\d+)?)%?", text, re.I)
        quality = float(quality_match.group(1)) if quality_match else 90.0

        target_price_match = re.search(r"(?:target|preferred|ideal)\s*price\s*(?:of|at|\$)?\s*(\$?\d+(?:\.\d+)?)", text, re.I)
        target_p = float(target_price_match.group(1).replace("$", "")) if target_price_match else (max_p * 0.9)
        if target_p > max_p:
            target_p = max_p * 0.9

        return BuyerRequirements(
            quantity=qty,
            max_price=max_p,
            min_quality=quality,
            max_delivery_days=days,
            target_price=target_p
        )
