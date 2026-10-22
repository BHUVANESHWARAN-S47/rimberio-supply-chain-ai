import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.agents.base import BaseAgent
from backend.app.agents.registry import AgentRegistry
from backend.app.schemas.common import AgentCapability
from backend.app.schemas.explanation import (
    ExplanationRequest,
    ExplanationResponse,
    ExplanationMode,
)
from backend.app.core.config import settings
from backend.app.core.llm import llm_service


class ExplanationAgent(BaseAgent[ExplanationRequest, ExplanationResponse]):
    """Natural Language & Causal Explanation AI Agent in RIMBERIO.

    Transforms deterministic multi-agent telemetry, counterfactual twin simulations,
    and Pareto tradeoffs into transparent, executive-ready briefings and interactive dialogue
    powered by Groq LLaMA-3.3-70B.
    """

    ADVERSARIAL_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"say\s+the\s+opposite", re.IGNORECASE),
        re.compile(r"system\s+prompt\s+override", re.IGNORECASE),
        re.compile(r"hallucinate\s+different\s+numbers", re.IGNORECASE),
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE),
        re.compile(r"(drop|delete|insert|update)\s+table", re.IGNORECASE),
    ]

    def __init__(self, db: Optional[Session] = None):
        super().__init__(
            name="Explanation Agent",
            description="Conversational synthesis and causal reasoning agent explaining multi-agent decisions via Groq LLaMA.",
            capabilities=[AgentCapability.EXPLANATION_SYNTHESIS],
        )
        self.db = db

    def validate_input(self, input_data: Any) -> ExplanationRequest:
        if isinstance(input_data, ExplanationRequest):
            return input_data
        elif isinstance(input_data, dict):
            return ExplanationRequest(**input_data)
        raise ValueError(f"Unsupported input type for ExplanationAgent: {type(input_data)}")

    def run_deterministic_logic(
        self,
        validated_input: ExplanationRequest,
        state: Optional[Any] = None,
    ) -> ExplanationResponse:
        return self._execute_deterministic(validated_input)

    def _execute_deterministic(
        self,
        req: ExplanationRequest,
    ) -> ExplanationResponse:
        # 1. Adversarial Defense
        cleaned_query = req.user_query or ""
        for pat in self.ADVERSARIAL_PATTERNS:
            cleaned_query = pat.sub("[FLAGGED_INPUT]", cleaned_query)

        # 2. Extract deterministic metrics
        dec_ctx = req.decision_context or {}
        cnt_ctx = req.counterfactual_context or {}
        cust_ctx = req.customer_impact_context or {}
        risk_ctx = req.risk_context or {}

        decision = dec_ctx.get("decision", "RETAIN")
        selected_sup = dec_ctx.get("selected_supplier", dec_ctx.get("selected_supplier_name", "Incumbent Supplier"))
        util_delta = dec_ctx.get("utility_delta", 0.0)
        net_financial = dec_ctx.get("net_financial_benefit", 0.0)

        cost_delta = cnt_ctx.get("cost_variance_pct", cnt_ctx.get("cost_delta", 0.0))
        lead_time_delta = cnt_ctx.get("lead_time_delta_days", 0)
        stockout_prob = cnt_ctx.get("stockout_probability", 0.0)

        sla_penalty = cust_ctx.get("total_sla_penalty_exposure", cust_ctx.get("sla_penalty", 0.0))
        churn_risk = cust_ctx.get("max_churn_risk", cust_ctx.get("churn_risk_score", 0.0))

        comp_risk = risk_ctx.get("composite_risk_score", risk_ctx.get("risk_score", 25.0))

        key_metrics = {
            "decision": decision,
            "selected_supplier": selected_sup,
            "utility_delta": util_delta,
            "net_financial_benefit": net_financial,
            "cost_variance_pct": cost_delta,
            "lead_time_delta_days": lead_time_delta,
            "stockout_probability": stockout_prob,
            "sla_penalty_exposure": sla_penalty,
            "churn_risk": churn_risk,
            "composite_risk": comp_risk,
        }

        # 3. Formulate Causal Points
        causal_points = []
        if decision == "SWITCH":
            causal_points.append(f"Switching to {selected_sup} generates a utility gain of +{util_delta:.2f} points over incumbent.")
            if net_financial > 0:
                causal_points.append(f"Projected net financial savings of ${net_financial:,.2f} justify the one-time transition overhead.")
            if comp_risk > 60:
                causal_points.append(f"Incumbent disruption risk ({comp_risk:.1f}/100) exceeded acceptable tolerance thresholds.")
        elif decision == "NEGOTIATE":
            causal_points.append(f"Incumbent agreement underperformed industry benchmark, but viable concession margins remain.")
            causal_points.append(f"Renegotiating avoids contractual switching friction while targeting price reductions.")
        else:
            causal_points.append(f"Retaining {selected_sup} preserves continuity and avoids transition downtime.")
            causal_points.append(f"Alternative supplier proposals did not clear the required margin hurdle.")

        if sla_penalty > 0:
            causal_points.append(f"Downstream customer SLA penalty liability estimated at ${sla_penalty:,.2f}.")

        # 4. Trade-off Analysis
        if decision == "SWITCH":
            tradeoffs = (
                f"Trade-Off: Accepting initial supplier switching overhead and qualification cycles in exchange for "
                f"long-term unit cost reductions ({cost_delta:+.1f}%) and superior resilience."
            )
        elif decision == "NEGOTIATE":
            tradeoffs = (
                f"Trade-Off: Investment of procurement negotiation cycles to preserve vendor relationship "
                f"vs immediately exercising alternative supply options."
            )
        else:
            tradeoffs = (
                f"Trade-Off: Prioritizing guaranteed fulfillment continuity and zero switching risk "
                f"over aggressive speculative cost cuts."
            )

        recommendations = [
            f"Formalize policy direction [{decision}] with executive procurement stakeholders.",
            f"Monitor customer SLA delivery buffers (Current penalty liability: ${sla_penalty:,.2f}).",
            f"Maintain secondary vendor qualifications as an active hedge against disruption.",
        ]

        title = f"RIMBERIO Strategic Briefing: Policy Decision [{decision}]"
        summary = (
            f"Autonomous multi-agent consensus recommends [{decision}] with supplier '{selected_sup}'. "
            f"Utility Delta: {util_delta:+.2f} pts | Risk Profile: {comp_risk:.1f}/100 | SLA Liability: ${sla_penalty:,.2f}."
        )

        # 5. Groq LLaMA Synthesis Prompt
        target_model = req.model_name or settings.DEFAULT_LLM_MODEL
        prompt_content = (
            f"Synthesize this supply chain decision debrief into an executive brief.\n"
            f"User Query: {cleaned_query}\n"
            f"Mode: {req.mode.value}\n"
            f"Key Metrics: {key_metrics}\n"
            f"Causal Points: {causal_points}\n"
            f"Tradeoffs: {tradeoffs}\n"
            f"Strict constraint: Preserve all numerical figures and decisions exactly as given."
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are the RIMBERIO Explanation Agent powered by Groq LLaMA. "
                    "You explain complex counterfactual supply chain simulations, risk metrics, and "
                    "negotiation outcomes with crystal clarity and zero hallucinations."
                ),
            },
            {
                "role": "user",
                "content": prompt_content,
            },
        ]

        deterministic_narrative = (
            f"### {title}\n\n"
            f"{summary}\n\n"
            f"#### Causal Rationale:\n"
            + "\n".join(f"- {pt}" for pt in causal_points)
            + f"\n\n#### Trade-Off Analysis:\n{tradeoffs}\n\n"
            f"#### Recommended Actions:\n"
            + "\n".join(f"1. {r}" for r in recommendations)
        )

        full_narrative = llm_service.generate_completion(
            messages=messages,
            fallback_response=deterministic_narrative,
            temperature=req.temperature,
            max_tokens=600,
            model=target_model,
        )

        return ExplanationResponse(
            title=title,
            summary=summary,
            causal_reasoning_points=causal_points,
            key_metrics_referenced=key_metrics,
            tradeoff_analysis=tradeoffs,
            actionable_recommendations=recommendations,
            full_narrative=full_narrative,
            model_used=target_model,
        )


AgentRegistry.register("explanation_agent", ExplanationAgent)
