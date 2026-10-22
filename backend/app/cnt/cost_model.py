from typing import Dict, Any, Optional
from backend.app.cnt.models import CostAssumptions, CostBreakdown


class CostModel:
    """Transparent deterministic supply chain cost calculation model.

    Computes total landed cost broken down into purchase, transportation,
    inventory holding, stockout penalties, quality failure, delivery delay,
    switching, and expediting costs without hidden LLM approximations.
    """

    def __init__(self, assumptions: Optional[CostAssumptions] = None):
        self.assumptions = assumptions or CostAssumptions()

    def calculate_cost(
        self,
        unit_price: float,
        quantity: int,
        transport_cost: float,
        average_inventory: float,
        stockout_quantity: float,
        defect_rate: float,
        expected_lead_time_days: float,
        baseline_lead_time_days: float,
        is_supplier_switch: bool,
        expedited_units: float = 0.0,
    ) -> CostBreakdown:
        """Computes comprehensive cost breakdown."""
        qty = max(0, quantity)
        unit_p = max(0.0, unit_price)

        # 1. Direct Purchase Cost
        purchase_cost = round(unit_p * qty, 2)

        # 2. Transportation Cost
        transportation_cost = round(max(0.0, transport_cost), 2)

        # 3. Inventory Holding Cost: (avg_inventory * unit_price * annual_rate * horizon_fraction)
        annual_rate = self.assumptions.holding_cost_annual_rate
        horizon_fraction = self.assumptions.time_horizon_days / 365.0
        holding_cost = round(max(0.0, average_inventory) * unit_p * annual_rate * horizon_fraction, 2)

        # 4. Stockout Cost: stockout units * penalty per unit
        stockout_cost = round(max(0.0, stockout_quantity) * self.assumptions.stockout_cost_per_unit, 2)

        # 5. Quality Failure Cost: defective units * unit cost * multiplier
        defective_units = qty * max(0.0, min(1.0, defect_rate))
        quality_failure_cost = round(
            defective_units * unit_p * self.assumptions.quality_failure_multiplier, 2
        )

        # 6. Delay Penalty Cost: days delayed * daily penalty
        delay_days = max(0.0, expected_lead_time_days - baseline_lead_time_days)
        delay_cost = round(delay_days * self.assumptions.delay_cost_per_day, 2)

        # 7. Supplier Switching Cost (One-time administrative/qualification burden)
        switching_cost = round(self.assumptions.switching_fixed_cost if is_supplier_switch else 0.0, 2)

        # 8. Expediting Cost: emergency expediting fees
        expediting_cost = round(max(0.0, expedited_units) * self.assumptions.expediting_fee_per_unit, 2)

        # 9. Total Landed Cost (sum of all constituent cost pillars)
        total_landed_cost = round(
            purchase_cost
            + transportation_cost
            + holding_cost
            + stockout_cost
            + quality_failure_cost
            + delay_cost
            + switching_cost
            + expediting_cost,
            2,
        )

        return CostBreakdown(
            purchase_cost=purchase_cost,
            transportation_cost=transportation_cost,
            holding_cost=holding_cost,
            stockout_cost=stockout_cost,
            quality_failure_cost=quality_failure_cost,
            delay_cost=delay_cost,
            switching_cost=switching_cost,
            expediting_cost=expediting_cost,
            total_landed_cost=total_landed_cost,
        )
