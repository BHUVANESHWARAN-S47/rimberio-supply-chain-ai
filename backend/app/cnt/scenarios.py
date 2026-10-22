from typing import List, Dict, Any, Optional
import uuid
from backend.app.cnt.models import (
    BaselineState,
    CandidateAgreement,
    CounterfactualScenario,
    ScenarioType,
)


class ScenarioGenerator:
    """Generates counterfactual scenarios while enforcing counterfactual state integrity.

    Keeps the baseline state controlled and auditable, altering only designated
    decision and exogenous shock variables.
    """

    @staticmethod
    def generate_scenarios(
        baseline: BaselineState,
        candidate_agreements: List[CandidateAgreement],
        scenario_types: Optional[List[ScenarioType]] = None,
    ) -> List[CounterfactualScenario]:
        """Generates all counterfactual combinations for the provided candidate agreements and scenario types."""
        types_to_run = scenario_types or [
            ScenarioType.NORMAL,
            ScenarioType.HIGH_DEMAND,
            ScenarioType.SUPPLIER_DELAY,
            ScenarioType.TRANSPORT_DISRUPTION,
            ScenarioType.INVENTORY_SHORTAGE,
            ScenarioType.COMPOUND_DISRUPTION,
        ]

        scenarios: List[CounterfactualScenario] = []

        for candidate in candidate_agreements:
            for sc_type in types_to_run:
                sc_id = f"SCEN-{candidate.supplier_code or candidate.supplier_id[:8]}-{sc_type.value}"

                # 1. Identify Changed Decision Variables
                changed_vars: Dict[str, Any] = {}
                if candidate.supplier_id != baseline.supplier_id:
                    changed_vars["supplier_id"] = candidate.supplier_id
                    changed_vars["supplier_name"] = candidate.company_name or candidate.supplier_code

                if candidate.proposed_unit_price != baseline.current_unit_price:
                    changed_vars["unit_price"] = candidate.proposed_unit_price
                    changed_vars["price_delta_pct"] = round(
                        ((candidate.proposed_unit_price - baseline.current_unit_price) / baseline.current_unit_price) * 100, 2
                    )

                if candidate.proposed_lead_time_days != baseline.current_lead_time_days:
                    changed_vars["lead_time_days"] = candidate.proposed_lead_time_days
                    changed_vars["lead_time_delta_days"] = candidate.proposed_lead_time_days - baseline.current_lead_time_days

                if candidate.proposed_quantity != baseline.current_quantity:
                    changed_vars["order_quantity"] = candidate.proposed_quantity

                # 2. Identify Unchanged Variables
                unchanged_vars = {
                    "product_id": baseline.product_id,
                    "product_sku": baseline.product_sku,
                    "current_inventory": baseline.current_inventory,
                    "safety_stock": baseline.safety_stock,
                    "daily_demand_mean": baseline.daily_demand_mean,
                    "pending_customer_orders_count": baseline.pending_customer_orders_count,
                    "active_shipments_count": baseline.active_shipments_count,
                }

                # 3. Define Exogenous Scenario Assumptions
                assumptions: Dict[str, Any] = {
                    "scenario_type": sc_type.value,
                    "demand_shock_multiplier": 1.0,
                    "lead_time_drift_days": 0.0,
                    "inventory_depletion_shock_units": 0,
                    "freight_surge_multiplier": 1.0,
                    "defect_shock_multiplier": 1.0,
                }

                if sc_type == ScenarioType.HIGH_DEMAND:
                    assumptions["demand_shock_multiplier"] = 1.40
                elif sc_type == ScenarioType.LOW_DEMAND:
                    assumptions["demand_shock_multiplier"] = 0.75
                elif sc_type == ScenarioType.SUPPLIER_DELAY:
                    assumptions["lead_time_drift_days"] = 5.0
                elif sc_type == ScenarioType.TRANSPORT_DISRUPTION:
                    assumptions["lead_time_drift_days"] = 4.0
                    assumptions["freight_surge_multiplier"] = 1.80
                elif sc_type == ScenarioType.PRICE_INCREASE:
                    changed_vars["unit_price"] = round(candidate.proposed_unit_price * 1.15, 2)
                elif sc_type == ScenarioType.INVENTORY_SHORTAGE:
                    assumptions["inventory_depletion_shock_units"] = int(baseline.current_inventory * 0.5)
                elif sc_type == ScenarioType.QUALITY_DEGRADATION:
                    assumptions["defect_shock_multiplier"] = 3.5
                elif sc_type == ScenarioType.CAPACITY_REDUCTION:
                    assumptions["capacity_reduction_pct"] = 0.50
                elif sc_type == ScenarioType.COMPOUND_DISRUPTION:
                    assumptions["demand_shock_multiplier"] = 1.30
                    assumptions["lead_time_drift_days"] = 6.0
                    assumptions["freight_surge_multiplier"] = 1.50
                    assumptions["inventory_depletion_shock_units"] = int(baseline.current_inventory * 0.4)

                desc = (
                    f"Counterfactual simulation of candidate {candidate.company_name or candidate.supplier_id} "
                    f"at ${candidate.proposed_unit_price:.2f}/unit ({candidate.proposed_lead_time_days}d lead time) "
                    f"under {sc_type.value} operational conditions."
                )

                scenarios.append(
                    CounterfactualScenario(
                        scenario_id=sc_id,
                        scenario_type=sc_type,
                        description=desc,
                        candidate_agreement=candidate,
                        changed_variables=changed_vars,
                        unchanged_variables=unchanged_vars,
                        scenario_assumptions=assumptions,
                    )
                )

        return scenarios
