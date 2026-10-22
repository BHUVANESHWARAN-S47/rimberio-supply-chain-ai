import numpy as np
from typing import Dict, Any, Optional, Tuple
from backend.app.cnt.models import ScenarioType


class QualityModel:
    """Predicts defect rates, non-conformance quantities, and quality costs."""

    def __init__(self, rng: Optional[np.random.RandomState] = None):
        self.rng = rng or np.random.RandomState(42)

    def estimate_quality_metrics(
        self,
        base_defect_rate: float,
        order_quantity: int,
        unit_cost: float,
        scenario_type: ScenarioType,
        quality_penalty_multiplier: float = 2.5,
    ) -> Tuple[float, float, float]:
        """Calculates expected defect rate, defective units, and quality loss.

        Returns: (effective_defect_rate, expected_defective_units, quality_failure_cost)
        """
        nominal_defect_rate = max(0.001, min(0.5, base_defect_rate))

        # Modulate by scenario
        if scenario_type == ScenarioType.QUALITY_DEGRADATION:
            effective_defect_rate = min(0.35, nominal_defect_rate * 3.5 + 0.05)
        elif scenario_type == ScenarioType.COMPOUND_DISRUPTION:
            effective_defect_rate = min(0.40, nominal_defect_rate * 2.5 + 0.03)
        else:
            effective_defect_rate = nominal_defect_rate

        expected_defective_units = round(order_quantity * effective_defect_rate, 2)
        quality_failure_cost = round(
            expected_defective_units * unit_cost * quality_penalty_multiplier, 2
        )

        return round(effective_defect_rate, 4), expected_defective_units, quality_failure_cost

    def sample_actual_defects(
        self,
        effective_defect_rate: float,
        order_quantity: int,
    ) -> int:
        """Stochastic binomial sample of defective items."""
        qty = max(0, order_quantity)
        p = max(0.0, min(1.0, effective_defect_rate))
        return int(self.rng.binomial(n=qty, p=p))
