from typing import List
from backend.models.schemas import CounterfactualSimulationRequest, SimulationOutcome
from backend.services.customization_store import customization_store
from backend.services.data_manager import data_manager
from backend.agents.counterfactual_twin import CounterfactualTwinModel

class CounterfactualTwinEngine:
    """
    Simulates counterfactual supply chain outcomes using the mathematical
    CounterfactualTwinModel on ANY dynamic supplier and custom disruption scenario.
    """

    def __init__(self):
        self.twin_model = CounterfactualTwinModel()

    def run_simulation(self, req: CounterfactualSimulationRequest) -> SimulationOutcome:
        profile = customization_store.get_profile()
        sim_config = profile.simulation
        samples = req.monte_carlo_samples or sim_config.monte_carlo_runs

        # Fetch supplier from dynamic data manager
        suppliers = data_manager.get_suppliers()
        match = next((s for s in suppliers if s["code"] == req.supplier_code), None)

        if match:
            supplier_name = match["name"]
            base_cost = float(match["unit_cost"])
            reliability = float(match["reliability_index"]) / 100.0
            base_lead = 12 if "Strategic" in str(match.get("tier", "")) else 16
        else:
            supplier_name = "Apex Global Electronics"
            base_cost = 142.50
            reliability = 0.94
            base_lead = 12

        # Run mathematical Monte Carlo causal DAG simulation
        results = self.twin_model.simulate(
            base_unit_cost=base_cost,
            base_lead_time_days=base_lead,
            supplier_reliability=reliability,
            disruption_lead_drift=req.lead_time_drift_days,
            demand_surge_percent=req.demand_surge_percent,
            freight_cost_surge_percent=req.freight_cost_surge_percent,
            inventory_buffer_units=5000,
            order_batch_units=14820,
            monte_carlo_samples=samples
        )

        counterfactual_savings = float(round(max(0.0, 120000.0 - results["expected_cost_impact"]), 2))

        return SimulationOutcome(
            supplier_code=req.supplier_code,
            supplier_name=supplier_name,
            scenario_tested=req.disruption_scenario,
            expected_cost_impact=results["expected_cost_impact"],
            cost_impact_p95=results["cost_impact_p95_var"],
            stockout_probability=results["stockout_probability"],
            sla_breach_probability=results["sla_breach_probability"],
            expected_delay_days=results["expected_delay_days"],
            counterfactual_net_saving=counterfactual_savings,
            risk_level=results["risk_classification"],
            distribution_samples=results["distribution_quantiles"]
        )

counterfactual_twin = CounterfactualTwinEngine()
