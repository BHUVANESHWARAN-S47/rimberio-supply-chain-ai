import numpy as np
from typing import Dict, Any, List, Optional
from backend.app.cnt.models import ScenarioType


class DemandModel:
    """Simulates customer demand dynamics, stochastic order shocks, and macro variations."""

    def __init__(self, rng: Optional[np.random.RandomState] = None):
        self.rng = rng or np.random.RandomState(42)

    def sample_daily_demands(
        self,
        mean_daily_demand: float,
        std_daily_demand: float,
        horizon_days: int,
        scenario_type: ScenarioType,
        surge_multiplier: float = 1.0,
    ) -> np.ndarray:
        """Generates stochastic daily demands over the simulation horizon."""
        h = max(1, horizon_days)
        base_mu = max(1.0, mean_daily_demand)
        base_sigma = max(0.1, std_daily_demand)

        # Modulate demand according to scenario
        if scenario_type == ScenarioType.HIGH_DEMAND:
            multiplier = 1.40 * surge_multiplier
            sigma_mult = 1.25
        elif scenario_type == ScenarioType.LOW_DEMAND:
            multiplier = 0.75 * surge_multiplier
            sigma_mult = 0.85
        elif scenario_type == ScenarioType.COMPOUND_DISRUPTION:
            multiplier = 1.30 * surge_multiplier
            sigma_mult = 1.50
        else:
            multiplier = 1.0 * surge_multiplier
            sigma_mult = 1.0

        eff_mu = base_mu * multiplier
        eff_sigma = base_sigma * sigma_mult

        samples = self.rng.normal(loc=eff_mu, scale=eff_sigma, size=h)
        # Demand cannot be physically negative
        return np.maximum(0.0, np.round(samples, 1))

    def calculate_total_lead_time_demand(
        self,
        daily_demands: np.ndarray,
        lead_time_days: int,
    ) -> float:
        """Sums demand that arrives during the supplier's fulfillment lead time window."""
        lt = max(1, min(len(daily_demands), int(np.ceil(lead_time_days))))
        return float(np.sum(daily_demands[:lt]))
