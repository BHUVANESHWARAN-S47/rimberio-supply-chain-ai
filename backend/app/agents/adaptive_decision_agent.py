import re
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.agents.base import BaseAgent
from backend.app.agents.registry import AgentRegistry
from backend.app.schemas.common import AgentCapability, DecisionAction
from backend.app.schemas.decision import (
    AdaptiveDecisionRequest,
    AdaptiveDecisionResponse,
    SupplierCandidateEvaluation,
)
from backend.app.database.models import (
    AdaptiveDecisionDB,
    SupplierComparisonDB,
    SupplierDB,
)
from backend.app.core.llm import llm_service


class AdaptiveDecisionAgent(BaseAgent[AdaptiveDecisionRequest, AdaptiveDecisionResponse]):
    """Enterprise Policy Decision Agent (RETAIN vs NEGOTIATE vs SWITCH).

    Executes Multi-Criteria Decision Analysis (MCDA) across price, quality, delivery,
    logistics, risk, and customer SLA exposure to select the globally optimal supplier policy.
    Zero-hallucination deterministic scoring with Groq LLaMA strategic reasoning.
    """

    ADVERSARIAL_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"force\s+(switch|retain|negotiate)", re.IGNORECASE),
        re.compile(r"ignore\s+switching\s+costs?", re.IGNORECASE),
        re.compile(r"bypass\s+risk\s+threshold", re.IGNORECASE),
        re.compile(r"set\s+decision\s+to", re.IGNORECASE),
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE),
        re.compile(r"(drop|delete|insert|update)\s+table", re.IGNORECASE),
    ]

    DEFAULT_WEIGHTS = {
        "price": 0.25,
        "quality": 0.20,
        "delivery": 0.15,
        "risk": 0.15,
        "logistics": 0.10,
        "customer_impact": 0.15,
    }

    def __init__(self, db: Optional[Session] = None):
        super().__init__(
            name="Adaptive Decision Agent",
            description="Autonomous policy arbitrator determining whether to RETAIN, NEGOTIATE, or SWITCH suppliers.",
            capabilities=[AgentCapability.POLICY_DECISION],
        )
        self.db = db

    def validate_input(self, input_data: Any) -> AdaptiveDecisionRequest:
        if isinstance(input_data, AdaptiveDecisionRequest):
            return input_data
        elif isinstance(input_data, dict):
            return AdaptiveDecisionRequest(**input_data)
        raise ValueError(f"Unsupported input type for AdaptiveDecisionAgent: {type(input_data)}")

    def run_deterministic_logic(
        self,
        validated_input: AdaptiveDecisionRequest,
        state: Optional[Any] = None,
    ) -> AdaptiveDecisionResponse:
        return self._execute_deterministic(validated_input)

    def _execute_deterministic(
        self,
        req: AdaptiveDecisionRequest,
    ) -> AdaptiveDecisionResponse:
        # 1. Weights normalization
        if req.weights:
            merged_weights = {k: float(req.weights.get(k, 0.0)) for k in self.DEFAULT_WEIGHTS.keys()}
            total_w = sum(merged_weights.values())
            if total_w > 0:
                weights = {k: v / total_w for k, v in merged_weights.items()}
            else:
                weights = dict(self.DEFAULT_WEIGHTS)
        else:
            weights = dict(self.DEFAULT_WEIGHTS)

        candidates = req.candidate_suppliers
        if not candidates:
            # Fallback candidate if empty
            candidates = [
                {
                    "supplier_id": req.incumbent_supplier_id,
                    "supplier_name": "Current Incumbent",
                    "price_score": 75.0,
                    "quality_score": 80.0,
                    "delivery_score": 80.0,
                    "risk_score": 30.0,
                    "logistics_score": 80.0,
                    "customer_impact_score": 85.0,
                }
            ]

        # 2. Evaluate each candidate's multi-criteria utility
        evaluated_candidates: List[SupplierCandidateEvaluation] = []
        incumbent_eval: Optional[SupplierCandidateEvaluation] = None

        for cand in candidates:
            sup_id = str(cand.get("supplier_id", f"SUP-{uuid.uuid4().hex[:6].upper()}"))
            is_incumbent = (sup_id == req.incumbent_supplier_id) or bool(cand.get("is_incumbent", False))
            sup_name = cand.get("supplier_name", f"Supplier {sup_id}")

            p_score = min(100.0, max(0.0, float(cand.get("price_score", 50.0))))
            q_score = min(100.0, max(0.0, float(cand.get("quality_score", 50.0))))
            d_score = min(100.0, max(0.0, float(cand.get("delivery_score", 50.0))))
            rel_score = min(100.0, max(0.0, float(cand.get("reliability_score", q_score))))
            risk_score = min(100.0, max(0.0, float(cand.get("risk_score", 25.0))))
            log_score = min(100.0, max(0.0, float(cand.get("logistics_score", 70.0))))
            cust_score = min(100.0, max(0.0, float(cand.get("customer_impact_score", 75.0))))
            sw_cost = max(0.0, float(cand.get("switching_cost", 0.0 if is_incumbent else 2500.0)))

            # Risk contribution: inverse of risk score (0 risk -> 100 points)
            risk_utility = 100.0 - risk_score

            raw_utility = (
                p_score * weights.get("price", 0.0)
                + q_score * weights.get("quality", 0.0)
                + d_score * weights.get("delivery", 0.0)
                + risk_utility * weights.get("risk", 0.0)
                + log_score * weights.get("logistics", 0.0)
                + cust_score * weights.get("customer_impact", 0.0)
            )

            # Switching cost deduction for non-incumbents
            sw_penalty = 0.0 if is_incumbent else min(15.0, sw_cost / 1000.0)
            overall_utility = round(max(0.0, min(100.0, raw_utility - sw_penalty)), 2)

            strengths = []
            weaknesses = []
            if p_score >= 80: strengths.append("Highly competitive pricing")
            elif p_score < 50: weaknesses.append("Unfavorable unit pricing")
            if q_score >= 85: strengths.append("Superior quality tier")
            elif q_score < 60: weaknesses.append("Substandard defect rate")
            if risk_score <= 25: strengths.append("Low operational risk")
            elif risk_score >= 60: weaknesses.append("Elevated disruption hazard")
            if log_score >= 80: strengths.append("Reliable freight transit")
            if cust_score < 50: weaknesses.append("Severe customer SLA exposure")

            cand_eval = SupplierCandidateEvaluation(
                supplier_id=sup_id,
                supplier_name=sup_name,
                is_incumbent=is_incumbent,
                price_score=p_score,
                quality_score=q_score,
                delivery_score=d_score,
                reliability_score=rel_score,
                risk_score=risk_score,
                logistics_score=log_score,
                customer_impact_score=cust_score,
                switching_cost=sw_cost,
                overall_utility=overall_utility,
                rank=1,
                strengths=strengths,
                weaknesses=weaknesses,
            )
            evaluated_candidates.append(cand_eval)
            if is_incumbent:
                incumbent_eval = cand_eval

        # 3. Sort candidates by overall utility descending
        evaluated_candidates.sort(key=lambda x: x.overall_utility, reverse=True)
        for idx, item in enumerate(evaluated_candidates, start=1):
            item.rank = idx

        best_candidate = evaluated_candidates[0]

        # 4. Decision Rule Arbitration
        incumbent = incumbent_eval or evaluated_candidates[-1]
        utility_delta = round(best_candidate.overall_utility - incumbent.overall_utility, 2)
        net_financial_benefit = round(
            (best_candidate.price_score - incumbent.price_score) * 100.0 - best_candidate.switching_cost,
            2
        )

        tradeoffs = []
        # Case A: Incumbent critical risk breach
        if incumbent.risk_score >= req.max_acceptable_risk and best_candidate.supplier_id != incumbent.supplier_id:
            decision = DecisionAction.SWITCH
            confidence = 0.95
            reasoning = (
                f"Incumbent supplier {incumbent.supplier_name} risk ({incumbent.risk_score:.1f}) exceeds the safety threshold "
                f"({req.max_acceptable_risk:.1f}). Mandatory SWITCH to {best_candidate.supplier_name}."
            )
            tradeoffs.append(f"Averting catastrophic disruption risk at incumbent ({incumbent.risk_score:.1f}/100)")

        # Case B: Best candidate exceeds incumbent utility by switching threshold
        elif best_candidate.supplier_id != incumbent.supplier_id and utility_delta >= req.switching_threshold_utility_gain:
            decision = DecisionAction.SWITCH
            confidence = min(0.98, round(0.80 + utility_delta * 0.015, 2))
            reasoning = (
                f"Alternate supplier {best_candidate.supplier_name} yields a significant utility surplus of +{utility_delta:.2f} points "
                f"(Utility: {best_candidate.overall_utility:.2f} vs Incumbent: {incumbent.overall_utility:.2f}), exceeding the {req.switching_threshold_utility_gain:.1f}pt switching barrier."
            )
            tradeoffs.append(f"Net utility gain of +{utility_delta:.2f} justified switching overhead of ${best_candidate.switching_cost:,.2f}")

        # Case C: Incumbent is best, or gap is narrow enough that negotiation is advantageous
        elif req.allow_negotiation and (
            utility_delta > 0 or incumbent.price_score < 75.0 or incumbent.overall_utility < 80.0
        ):
            decision = DecisionAction.NEGOTIATE
            confidence = 0.88
            selected_candidate = incumbent
            reasoning = (
                f"Current supplier agreement underperforms benchmark terms. Concession window exists. "
                f"Policy recommends NEGOTIATE with {incumbent.supplier_name} before committing switching friction."
            )
            tradeoffs.append(f"Preserving existing buyer-supplier relationship while extracting price/delivery concessions")
            best_candidate = incumbent  # Remain with incumbent during negotiation

        # Case D: RETAIN incumbent
        else:
            decision = DecisionAction.RETAIN
            confidence = 0.92
            best_candidate = incumbent
            reasoning = (
                f"Incumbent supplier {incumbent.supplier_name} remains optimal (Utility: {incumbent.overall_utility:.2f}). "
                f"Alternative suppliers do not deliver sufficient margin to offset transition friction."
            )
            tradeoffs.append("Zero switching downtime or contract renegotiation overhead")

        # 5. Persist to DB if session provided
        if self.db and req.simulation_run_id:
            self._persist_decision(req, decision, best_candidate, confidence, reasoning, evaluated_candidates)

        # 6. Executive summary via Groq LLaMA
        exec_summary = self._generate_executive_summary(
            decision=decision,
            selected_name=best_candidate.supplier_name,
            confidence=confidence,
            utility_delta=utility_delta,
            reasoning=reasoning,
        )

        return AdaptiveDecisionResponse(
            decision=decision,
            selected_supplier_id=best_candidate.supplier_id,
            selected_supplier_name=best_candidate.supplier_name,
            confidence=confidence,
            utility_delta=utility_delta,
            net_financial_benefit=net_financial_benefit,
            supplier_rankings=evaluated_candidates,
            key_tradeoffs=tradeoffs,
            reasoning=reasoning,
            executive_summary=exec_summary,
        )

    def _persist_decision(
        self,
        req: AdaptiveDecisionRequest,
        decision: DecisionAction,
        selected: SupplierCandidateEvaluation,
        confidence: float,
        reasoning: str,
        rankings: List[SupplierCandidateEvaluation],
    ):
        try:
            sim_id = uuid.UUID(req.simulation_run_id) if isinstance(req.simulation_run_id, str) else req.simulation_run_id
            try:
                sup_uuid = uuid.UUID(selected.supplier_id)
            except Exception:
                sup_uuid = uuid.uuid4()

            db_dec = AdaptiveDecisionDB(
                simulation_run_id=sim_id,
                selected_supplier_id=sup_uuid,
                decision_type=decision.value,
                confidence=confidence,
                reasoning=reasoning,
                decision_factors={
                    "utility_delta": selected.overall_utility,
                    "rank": selected.rank,
                    "price_score": selected.price_score,
                    "risk_score": selected.risk_score,
                },
            )
            self.db.add(db_dec)

            for cand in rankings:
                try:
                    cand_uuid = uuid.UUID(cand.supplier_id)
                except Exception:
                    cand_uuid = uuid.uuid4()
                db_comp = SupplierComparisonDB(
                    simulation_run_id=sim_id,
                    supplier_id=cand_uuid,
                    price_score=cand.price_score,
                    quality_score=cand.quality_score,
                    delivery_score=cand.delivery_score,
                    reliability_score=cand.reliability_score,
                    risk_score=cand.risk_score,
                    logistics_score=cand.logistics_score,
                    customer_impact_score=cand.customer_impact_score,
                    overall_score=cand.overall_utility,
                    rank=cand.rank,
                    explanation=f"Rank {cand.rank} with utility {cand.overall_utility:.2f}",
                )
                self.db.add(db_comp)
            self.db.commit()
        except Exception:
            if self.db:
                self.db.rollback()

    def _generate_executive_summary(
        self,
        decision: DecisionAction,
        selected_name: str,
        confidence: float,
        utility_delta: float,
        reasoning: str,
    ) -> str:
        base_summary = (
            f"Strategic Policy Arbitration: Recommendation is [{decision.value}] (Selected: {selected_name}, "
            f"Confidence: {confidence * 100:.1f}%, Utility Delta: {utility_delta:+.2f} pts). {reasoning}"
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are the RIMBERIO Strategic Adaptive Decision AI Agent. "
                    "Draft an executive briefing for supply chain leadership. "
                    "Preserve all decisions and numeric values exactly."
                ),
            },
            {
                "role": "user",
                "content": f"Synthesize this supplier arbitration decision into an executive brief:\n{base_summary}",
            },
        ]
        return llm_service.generate_completion(
            messages=messages,
            fallback_response=base_summary,
            max_tokens=300,
        )


AgentRegistry.register("adaptive_decision_agent", AdaptiveDecisionAgent)
