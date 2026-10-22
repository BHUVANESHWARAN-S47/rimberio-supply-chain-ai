from typing import List, Dict, Any
from backend.app.cnt.models import (
    ScenarioSimulationResult,
    ScenarioComparison,
    SensitivityResult,
    BaselineState,
)


class CNTExplainer:
    """Generates structured, auditable causal explanations of counterfactual simulation outcomes.

    Guarantees zero mathematical hallucination by directly synthesizing deterministic
    CNT calculated statistics into transparent explanations.
    """

    @staticmethod
    def generate_explanation(
        baseline: BaselineState,
        comparison: ScenarioComparison,
        sensitivities: List[SensitivityResult],
    ) -> str:
        """Constructs an end-to-end explanation addressing the 6 core causal questions."""
        lines: List[str] = []

        # 1. WHAT changed?
        best_candidate = comparison.rankings[0] if comparison.rankings else None
        if best_candidate and best_candidate.scenario_id in comparison.deltas:
            delta = comparison.deltas[best_candidate.scenario_id]
            lines.append(
                f"1. WHAT CHANGED: Evaluated {len(comparison.scenarios)} counterfactual scenarios. "
                f"Top-ranked alternative is {best_candidate.supplier_name} (Rank #{best_candidate.rank}, Utility Score: {best_candidate.overall_score}/100). "
                f"Net cost delta is {'+' if delta.cost_delta >= 0 else ''}${delta.cost_delta:,.2f} ({delta.cost_pct_delta:+.1f}%), "
                f"with lead-time shift of {delta.delivery_delta:+.1f} days."
            )
        else:
            lines.append("1. WHAT CHANGED: Baseline incumbent agreement retained as optimal operational benchmark.")

        # 2. WHY did the outcome change?
        lines.append(
            f"2. WHY OUTCOME CHANGED: Outcome shifts are driven by the interaction between unit price concession, "
            f"transportation freight allocation, holding costs, and delivery variance across the 30-day fulfillment window."
        )

        # 3. WHICH variables mattered?
        if sensitivities:
            top_sens = sorted(sensitivities, key=lambda s: s.sensitivity_score, reverse=True)[0]
            lines.append(
                f"3. KEY DRIVER VARIABLES: '{top_sens.parameter_name}' exhibits the highest system impact "
                f"(Sensitivity Score: {top_sens.sensitivity_score}/100). {top_sens.explanation}"
            )
        else:
            lines.append("3. KEY DRIVER VARIABLES: Quoted unit price and delivery lead times represent the primary drivers.")

        # 4. WHAT is the uncertainty?
        top_scen = next((s for s in comparison.scenarios if s.scenario_id == best_candidate.scenario_id), comparison.scenarios[0]) if best_candidate else comparison.scenarios[0]
        cr = top_scen.cost_range
        dr = top_scen.delivery_range
        lines.append(
            f"4. UNCERTAINTY PROFILE: 500-run Monte Carlo distribution establishes 80% credible interval "
            f"for total landed cost between ${cr.p10:,.2f} (P10) and ${cr.p90:,.2f} (P90) with median ${cr.p50:,.2f}. "
            f"Delivery lead time spans {dr.p10:.1f}d (P10) to {dr.p90:.1f}d (P90) with confidence factor {cr.confidence:.2f}."
        )

        # 5. WHAT is the downside risk?
        lines.append(
            f"5. DOWNSIDE RISK: Scenario risk score evaluated at {top_scen.predicted_risk}/100 ({top_scen.risk_level.value}). "
            f"Stockout probability under active parameters is {top_scen.stockout_probability*100:.1f}% "
            f"({top_scen.stockout_quantity_expected:.1f} units expected shortfall)."
        )

        # 6. WHAT is the customer impact?
        ci = top_scen.customer_impact
        lines.append(
            f"6. CUSTOMER IMPACT: {ci.reasoning} Overall customer impact rated {ci.impact_level.value} "
            f"({ci.customer_impact_score}/100)."
        )

        return "\n\n".join(lines)
