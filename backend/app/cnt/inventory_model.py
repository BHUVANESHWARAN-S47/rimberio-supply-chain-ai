import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from backend.app.cnt.models import ScenarioType


class InventoryModel:
    """Simulates dynamic warehouse stock depletion, buffer buffers, and stockout hazards.

    Guarantees physical conservation constraints: inventory never drops below zero.
    """

    def simulate_inventory_trajectory(
        self,
        opening_inventory: int,
        incoming_quantity: int,
        daily_demands: np.ndarray,
        actual_lead_time_days: float,
        safety_stock: int,
        scenario_type: ScenarioType,
        inventory_shock_units: int = 0,
    ) -> Tuple[int, float, float, float]:
        """Simulates stock trajectory over the fulfillment window and horizon.

        Returns:
            (closing_inventory, average_inventory, stockout_units, stockout_rate)
        """
        # Starting inventory after scenario shock if applicable
        starting_inv = max(0, opening_inventory)
        if scenario_type == ScenarioType.INVENTORY_SHORTAGE:
            starting_inv = max(0, int(starting_inv * 0.4) - inventory_shock_units)
        elif scenario_type == ScenarioType.COMPOUND_DISRUPTION:
            starting_inv = max(0, int(starting_inv * 0.6) - inventory_shock_units)

        horizon = len(daily_demands)
        arrival_day = int(np.ceil(actual_lead_time_days))

        current_stock = float(starting_inv)
        stock_levels: List[float] = []
        stockout_occurrences = 0
        total_unmet_demand = 0.0

        for day in range(horizon):
            # Arrival of supplier replenishment on arrival day
            if day == arrival_day:
                current_stock += max(0, incoming_quantity)

            demand_today = daily_demands[day]

            if current_stock >= demand_today:
                current_stock -= demand_today
            else:
                unmet = demand_today - current_stock
                total_unmet_demand += unmet
                current_stock = 0.0
                stockout_occurrences += 1

            stock_levels.append(current_stock)

        closing_inventory = int(np.round(current_stock))
        average_inventory = float(np.mean(stock_levels)) if stock_levels else float(starting_inv)
        stockout_rate = float(stockout_occurrences / horizon) if horizon > 0 else 0.0

        return (
            closing_inventory,
            round(average_inventory, 2),
            round(total_unmet_demand, 2),
            round(min(1.0, stockout_rate), 4),
        )

    def calculate_days_of_supply(
        self,
        inventory_units: int,
        mean_daily_demand: float,
    ) -> float:
        """Calculates days of inventory coverage."""
        d = max(0.1, mean_daily_demand)
        return round(max(0, inventory_units) / d, 1)
