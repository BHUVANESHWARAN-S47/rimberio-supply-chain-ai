import numpy as np
from typing import List, Dict, Any, Optional
from backend.app.cnt.models import (
    BaselineState,
    CounterfactualScenario,
    SimulationConfig,
    ScenarioSimulationResult,
    CostBreakdown,
)
from backend.app.cnt.cost_model import CostModel
from backend.app.cnt.demand_model import DemandModel
from backend.app.cnt.delivery_model import DeliveryModel
from backend.app.cnt.quality_model import QualityModel
from backend.app.cnt.inventory_model import InventoryModel
from backend.app.cnt.risk_model import RiskModel
from backend.app.cnt.customer_model import CustomerImpactModel
from backend.app.cnt.uncertainty import UncertaintyEngine


class CNTSimulator:
    """Core simulation engine performing vectorized Monte Carlo iterations in memory."""

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self.cost_model = CostModel(self.config.cost_assumptions)
        self.risk_model = RiskModel()
        self.customer_model = CustomerImpactModel()

    def simulate_scenario(
        self,
        baseline: BaselineState,
        scenario: CounterfactualScenario,
        pending_orders: Optional[List[Dict[str, Any]]] = None,
    ) -> ScenarioSimulationResult:
        """Simulates a single counterfactual scenario across N Monte Carlo iterations."""
        candidate = scenario.candidate_agreement
        assumptions = scenario.scenario_assumptions
        n_runs = self.config.num_monte_carlo_runs
        seed = self.config.random_seed

        # Initialize RNGs with deterministic seed
        rng = np.random.RandomState(seed)
        demand_model = DemandModel(rng=rng)
        delivery_model = DeliveryModel(rng=rng)
        quality_model = QualityModel(rng=rng)
        inventory_model = InventoryModel()

        # 1. Base Expected Lead Time & Distribution
        exp_lead_time, lt_std, delay_prob = delivery_model.estimate_lead_time_distribution(
            nominal_lead_time_days=candidate.proposed_lead_time_days,
            historical_lead_time_std=baseline.supplier_lead_time_std,
            supplier_reliability=baseline.supplier_historical_reliability if candidate.is_incumbent else (candidate.proposed_quality_score / 100.0 * 0.95),
            scenario_type=scenario.scenario_type,
            transport_delay_days=assumptions.get("lead_time_drift_days", 0.0),
        )

        # 2. Base Quality Expectation
        eff_defect_rate, exp_defects, _ = quality_model.estimate_quality_metrics(
            base_defect_rate=baseline.supplier_historical_defect_rate if candidate.is_incumbent else ((100.0 - candidate.proposed_quality_score) / 100.0 * 0.5),
            order_quantity=candidate.proposed_quantity,
            unit_cost=candidate.proposed_unit_price,
            scenario_type=scenario.scenario_type,
            quality_penalty_multiplier=self.config.cost_assumptions.quality_failure_multiplier,
        )

        # 3. Vectorized Monte Carlo Trial Buffers
        trial_costs = np.zeros(n_runs)
        trial_lead_times = np.zeros(n_runs)
        trial_closing_invs = np.zeros(n_runs)
        trial_stockout_units = np.zeros(n_runs)
        trial_stockout_rates = np.zeros(n_runs)
        trial_holding_costs = np.zeros(n_runs)
        trial_delay_costs = np.zeros(n_runs)
        trial_quality_costs = np.zeros(n_runs)

        horizon = self.config.cost_assumptions.time_horizon_days
        is_switch = (candidate.supplier_id != baseline.supplier_id) and not candidate.is_incumbent
        freight_cost = candidate.transport_cost * assumptions.get("freight_surge_multiplier", 1.0)

        for i in range(n_runs):
            # Sample lead time
            actual_lt = delivery_model.sample_actual_lead_time(
                expected_lead_time=exp_lead_time,
                lead_time_std=lt_std,
            )
            trial_lead_times[i] = actual_lt

            # Sample daily demand curve
            demands = demand_model.sample_daily_demands(
                mean_daily_demand=baseline.daily_demand_mean,
                std_daily_demand=baseline.daily_demand_std,
                horizon_days=horizon,
                scenario_type=scenario.scenario_type,
                surge_multiplier=assumptions.get("demand_shock_multiplier", 1.0),
            )

            # Sample inventory trajectory
            closing_inv, avg_inv, stockout_units, stockout_rate = inventory_model.simulate_inventory_trajectory(
                opening_inventory=baseline.current_inventory,
                incoming_quantity=candidate.proposed_quantity,
                daily_demands=demands,
                actual_lead_time_days=actual_lt,
                safety_stock=baseline.safety_stock,
                scenario_type=scenario.scenario_type,
                inventory_shock_units=assumptions.get("inventory_depletion_shock_units", 0),
            )
            trial_closing_invs[i] = closing_inv
            trial_stockout_units[i] = stockout_units
            trial_stockout_rates[i] = stockout_rate

            # Sample defect rate
            actual_defects = quality_model.sample_actual_defects(
                effective_defect_rate=eff_defect_rate,
                order_quantity=candidate.proposed_quantity,
            )
            sim_defect_rate = actual_defects / max(1, candidate.proposed_quantity)

            # Calculate cost breakdown for trial
            cb = self.cost_model.calculate_cost(
                unit_price=candidate.proposed_unit_price,
                quantity=candidate.proposed_quantity,
                transport_cost=freight_cost,
                average_inventory=avg_inv,
                stockout_quantity=stockout_units,
                defect_rate=sim_defect_rate,
                expected_lead_time_days=actual_lt,
                baseline_lead_time_days=baseline.current_lead_time_days,
                is_supplier_switch=is_switch,
            )
            trial_costs[i] = cb.total_landed_cost
            trial_holding_costs[i] = cb.holding_cost
            trial_delay_costs[i] = cb.delay_cost
            trial_quality_costs[i] = cb.quality_failure_cost

        # 4. Uncertainty Distribution Aggregations
        cost_range = UncertaintyEngine.aggregate_distribution(trial_costs)
        delivery_range = UncertaintyEngine.aggregate_distribution(trial_lead_times)

        mean_stockout_rate = float(np.mean(trial_stockout_rates))
        mean_stockout_units = float(np.mean(trial_stockout_units))
        mean_closing_inv = int(np.round(np.mean(trial_closing_invs)))
        mean_delivery_delay = max(0.0, delivery_range.mean - baseline.current_lead_time_days)

        # 5. Customer Impact Evaluation
        customer_impact = self.customer_model.evaluate_customer_impact(
            pending_orders=pending_orders or [],
            stockout_rate=mean_stockout_rate,
            stockout_units=mean_stockout_units,
            actual_lead_time_days=delivery_range.mean,
            baseline_lead_time_days=baseline.current_lead_time_days,
            unit_price=candidate.proposed_unit_price,
        )

        # 6. Risk Scoring
        lead_time_cv = lt_std / max(1.0, exp_lead_time)
        days_of_supply = inventory_model.calculate_days_of_supply(
            inventory_units=mean_closing_inv,
            mean_daily_demand=baseline.daily_demand_mean,
        )
        risk_score, risk_level, confidence, risk_factors = self.risk_model.evaluate_risk(
            supplier_reliability=baseline.supplier_historical_reliability if candidate.is_incumbent else (candidate.proposed_quality_score / 100.0 * 0.95),
            lead_time_cv=lead_time_cv,
            defect_rate=eff_defect_rate,
            order_quantity=candidate.proposed_quantity,
            supplier_capacity=candidate.proposed_capacity or baseline.supplier_capacity,
            days_of_supply=days_of_supply,
            target_days_of_supply=25.0,
            scenario_type=scenario.scenario_type,
            disruption_history_events_count=0 if not candidate.is_incumbent else 1,
        )

        # 7. Aggregate Representative Cost Breakdown
        rep_cost_breakdown = CostBreakdown(
            purchase_cost=round(candidate.proposed_unit_price * candidate.proposed_quantity, 2),
            transportation_cost=round(freight_cost, 2),
            holding_cost=round(float(np.mean(trial_holding_costs)), 2),
            stockout_cost=round(mean_stockout_units * self.config.cost_assumptions.stockout_cost_per_unit, 2),
            quality_failure_cost=round(float(np.mean(trial_quality_costs)), 2),
            delay_cost=round(float(np.mean(trial_delay_costs)), 2),
            switching_cost=round(self.config.cost_assumptions.switching_fixed_cost if is_switch else 0.0, 2),
            expediting_cost=0.0,
            total_landed_cost=cost_range.mean,
        )

        # Service level
        service_level = round(max(50.0, min(100.0, 100.0 - (mean_stockout_rate * 60.0) - (mean_delivery_delay * 1.5))), 1)

        return ScenarioSimulationResult(
            scenario_id=scenario.scenario_id,
            scenario_type=scenario.scenario_type,
            candidate_supplier_id=candidate.supplier_id,
            candidate_supplier_name=candidate.company_name or candidate.supplier_code or candidate.supplier_id,
            predicted_cost=cost_range.mean,
            cost_range=cost_range,
            cost_breakdown=rep_cost_breakdown,
            predicted_delivery_days=delivery_range.mean,
            delivery_range=delivery_range,
            predicted_delivery_delay=round(mean_delivery_delay, 1),
            stockout_probability=round(mean_stockout_rate, 4),
            stockout_quantity_expected=round(mean_stockout_units, 1),
            predicted_inventory=mean_closing_inv,
            predicted_risk=risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            predicted_service_level=service_level,
            customer_impact=customer_impact,
            confidence=confidence,
            changed_variables=scenario.changed_variables,
            unchanged_variables=scenario.unchanged_variables,
            scenario_assumptions=scenario.scenario_assumptions,
        )
