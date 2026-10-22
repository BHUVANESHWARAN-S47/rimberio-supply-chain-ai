from typing import List, Dict, Any, Tuple, Optional
from backend.app.cnt.models import (
    ScenarioSimulationResult,
    ComparisonMetricDelta,
    RankedCandidate,
    ScenarioComparison,
    MultiObjectiveWeights,
)


class ScenarioComparator:
    """Performs multi-scenario comparative benchmarking, Pareto frontier detection, and candidate ranking."""

    def __init__(self, weights: Optional[MultiObjectiveWeights] = None):
        self.weights = weights or MultiObjectiveWeights()

    def compare_scenarios(
        self,
        baseline_result: ScenarioSimulationResult,
        candidate_results: List[ScenarioSimulationResult],
    ) -> ScenarioComparison:
        """Calculates deltas against baseline, identifies Pareto front, and ranks alternatives."""
        all_results = [baseline_result] + [r for r in candidate_results if r.scenario_id != baseline_result.scenario_id]

        deltas: Dict[str, ComparisonMetricDelta] = {}

        for res in all_results:
            cost_d = round(res.predicted_cost - baseline_result.predicted_cost, 2)
            cost_pct_d = (
                round((cost_d / baseline_result.predicted_cost) * 100, 2)
                if baseline_result.predicted_cost > 0
                else 0.0
            )

            deliv_d = round(res.predicted_delivery_days - baseline_result.predicted_delivery_days, 1)
            deliv_pct_d = (
                round((deliv_d / baseline_result.predicted_delivery_days) * 100, 2)
                if baseline_result.predicted_delivery_days > 0
                else 0.0
            )

            risk_d = round(res.predicted_risk - baseline_result.predicted_risk, 1)
            inv_d = res.predicted_inventory - baseline_result.predicted_inventory
            sl_d = round(res.predicted_service_level - baseline_result.predicted_service_level, 2)
            ci_d = round(res.customer_impact.customer_impact_score - baseline_result.customer_impact.customer_impact_score, 1)

            deltas[res.scenario_id] = ComparisonMetricDelta(
                cost_delta=cost_d,
                cost_pct_delta=cost_pct_d,
                delivery_delta=deliv_d,
                delivery_pct_delta=deliv_pct_d,
                risk_delta=risk_d,
                inventory_delta=inv_d,
                service_level_delta=sl_d,
                customer_impact_delta=ci_d,
            )

        # 2. Pareto Frontier Detection (Minimizing Cost, Delivery, Risk, Customer Impact; Maximizing Service Level)
        pareto_ids = self._find_pareto_frontier(all_results)

        # 3. Multi-Objective Scoring & Ranking
        ranked_candidates = self._rank_candidates(all_results, pareto_ids, baseline_result)

        return ScenarioComparison(
            baseline_scenario_id=baseline_result.scenario_id,
            scenarios=all_results,
            deltas=deltas,
            pareto_frontier=pareto_ids,
            rankings=ranked_candidates,
        )

    def _find_pareto_frontier(self, results: List[ScenarioSimulationResult]) -> List[str]:
        """Identifies non-dominated candidate scenarios across cost, delivery, and risk."""
        pareto_frontier: List[str] = []

        for candidate in results:
            is_dominated = False
            for other in results:
                if candidate.scenario_id == other.scenario_id:
                    continue

                # 'other' dominates 'candidate' if it is <= on bad metrics and >= on good metrics, and strictly better on at least one
                strictly_better_or_equal = (
                    other.predicted_cost <= candidate.predicted_cost
                    and other.predicted_delivery_days <= candidate.predicted_delivery_days
                    and other.predicted_risk <= candidate.predicted_risk
                    and other.predicted_service_level >= candidate.predicted_service_level
                )
                strictly_better_on_one = (
                    other.predicted_cost < candidate.predicted_cost
                    or other.predicted_delivery_days < candidate.predicted_delivery_days
                    or other.predicted_risk < candidate.predicted_risk
                    or other.predicted_service_level > candidate.predicted_service_level
                )

                if strictly_better_or_equal and strictly_better_on_one:
                    is_dominated = True
                    break

            if not is_dominated:
                pareto_frontier.append(candidate.scenario_id)

        return pareto_frontier

    def _rank_candidates(
        self,
        results: List[ScenarioSimulationResult],
        pareto_ids: List[str],
        baseline: ScenarioSimulationResult,
    ) -> List[RankedCandidate]:
        """Calculates multi-objective utility scores and ranks alternatives."""
        if not results:
            return []

        # Find min/max for normalization
        costs = [r.predicted_cost for r in results]
        deliveries = [r.predicted_delivery_days for r in results]
        risks = [r.predicted_risk for r in results]
        services = [r.predicted_service_level for r in results]

        min_c, max_c = min(costs), max(costs)
        min_d, max_d = min(deliveries), max(deliveries)
        min_r, max_r = min(risks), max(risks)
        min_s, max_s = min(services), max(services)

        scored: List[RankedCandidate] = []

        for res in results:
            # Normalize 0 to 100 where 100 is best
            price_score = 100.0 if max_c == min_c else round(((max_c - res.predicted_cost) / (max_c - min_c)) * 100.0, 1)
            delivery_score = 100.0 if max_d == min_d else round(((max_d - res.predicted_delivery_days) / (max_d - min_d)) * 100.0, 1)
            risk_score = 100.0 if max_r == min_r else round(((max_r - res.predicted_risk) / (max_r - min_r)) * 100.0, 1)
            service_score = 100.0 if max_s == min_s else round(((res.predicted_service_level - min_s) / (max_s - min_s)) * 100.0, 1)
            quality_score = round(max(0.0, min(100.0, (1.0 - res.stockout_probability) * 100.0)), 1)
            reliability_score = round(100.0 - res.predicted_risk, 1)

            # Weighted utility
            w = self.weights
            overall = round(
                (price_score * w.cost_weight)
                + (delivery_score * w.delivery_weight)
                + (risk_score * w.risk_weight)
                + (service_score * w.service_weight)
                + (quality_score * w.quality_weight)
                + (reliability_score * w.reliability_weight),
                1,
            )

            is_pareto = res.scenario_id in pareto_ids
            cost_diff = res.predicted_cost - baseline.predicted_cost
            rationale = (
                f"Overall utility score {overall}/100. "
                f"Cost: ${res.predicted_cost:,.2f} ({'+' if cost_diff>=0 else ''}{cost_diff:,.2f} vs baseline), "
                f"Lead time: {res.predicted_delivery_days:.1f}d, Risk: {res.predicted_risk:.1f}/100. "
                f"{'Pareto-efficient trade-off.' if is_pareto else 'Dominated by alternative candidates.'}"
            )

            scored.append(
                RankedCandidate(
                    rank=1,  # updated below
                    scenario_id=res.scenario_id,
                    supplier_id=res.candidate_supplier_id,
                    supplier_name=res.candidate_supplier_name,
                    overall_score=overall,
                    price_score=price_score,
                    delivery_score=delivery_score,
                    quality_score=quality_score,
                    reliability_score=reliability_score,
                    risk_score=risk_score,
                    service_score=service_score,
                    is_pareto_optimal=is_pareto,
                    recommendation_rationale=rationale,
                )
            )

        # Sort descending by overall score
        scored.sort(key=lambda x: x.overall_score, reverse=True)
        for idx, item in enumerate(scored):
            item.rank = idx + 1

        return scored
