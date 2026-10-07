import numpy as np
from typing import Dict, Any, List, Optional

class CounterfactualTwinModel:
    """
    Counterfactual Negotiation Twin (CNT) Mathematical Simulation Model.
    Performs causal Monte Carlo DAG evaluations on ANY arbitrary supply chain parameters:
    - Any candidate supplier pricing & lead time
    - Any inventory buffer level
    - Any disruption shock (chokepoints, demand surges, freight increases)
    - Computes empirical P95 VaR, Stockout Risk, and SLA Breach Probability
    """

    def simulate(
        self,
        base_unit_cost: float,
        base_lead_time_days: int,
        supplier_reliability: float,  # 0.0 to 1.0
        disruption_lead_drift: int,
        demand_surge_percent: float,
        freight_cost_surge_percent: float,
        inventory_buffer_units: int = 5000,
        order_batch_units: int = 14820,
        monte_carlo_samples: int = 1000
    ) -> Dict[str, Any]:
        """
        Runs stochastic simulation on ANY input parameters and returns distribution metrics.
        """
        n = max(50, monte_carlo_samples)

        # 1. Stochastic delay perturbation ~ Poisson distribution modulated by supplier reliability
        lambda_drift = max(0.5, disruption_lead_drift * (1.3 - supplier_reliability))
        simulated_delays = np.random.poisson(lam=lambda_drift, size=n)

        # 2. Total transit time per trial
        transit_times = base_lead_time_days + simulated_delays

        # 3. Freight and cost perturbations ~ Normal variance
        demand_multiplier = 1.0 + (demand_surge_percent / 100.0)
        freight_shocks = np.random.normal(loc=1.0 + (freight_cost_surge_percent / 100.0), scale=0.06, size=n)
        
        # Landed cost per trial = (unit_cost * demand_multiplier * freight_shock) * batch_size
        landed_costs = (base_unit_cost * demand_multiplier * freight_shocks) * order_batch_units
        baseline_cost = base_unit_cost * order_batch_units
        cost_impacts = landed_costs - baseline_cost

        # 4. Stockout calculation: if transit delay > buffer threshold
        # Assuming inventory buffer covers (inventory_buffer_units / daily_demand) days
        daily_demand = order_batch_units / 30.0
        buffer_coverage_days = inventory_buffer_units / max(1.0, daily_demand)
        stockout_mask = simulated_delays > buffer_coverage_days
        stockout_prob = float(round((np.sum(stockout_mask) / n) * 100.0, 2))

        # 5. SLA breach calculation (e.g. SLA tolerance = base_lead + 3 days)
        sla_limit = base_lead_time_days + 3
        sla_mask = transit_times > sla_limit
        sla_breach_prob = float(round((np.sum(sla_mask) / n) * 100.0, 2))

        mean_cost_impact = float(np.mean(cost_impacts))
        p95_cost_impact = float(np.percentile(cost_impacts, 95))
        p99_cost_impact = float(np.percentile(cost_impacts, 99))
        mean_delay = float(np.mean(simulated_delays))

        # Downsample for distribution charts (20 points)
        quantiles = [float(round(q, 2)) for q in np.percentile(cost_impacts, np.linspace(5, 95, 20))]

        return {
            "monte_carlo_samples": n,
            "expected_cost_impact": round(mean_cost_impact, 2),
            "cost_impact_p95_var": round(p95_cost_impact, 2),
            "cost_impact_p99_var": round(p99_cost_impact, 2),
            "stockout_probability": stockout_prob,
            "sla_breach_probability": sla_breach_prob,
            "expected_delay_days": round(mean_delay, 2),
            "buffer_coverage_days": round(buffer_coverage_days, 1),
            "distribution_quantiles": quantiles,
            "risk_classification": "CRITICAL" if sla_breach_prob > 35.0 else ("MODERATE" if sla_breach_prob > 12.0 else "LOW")
        }
