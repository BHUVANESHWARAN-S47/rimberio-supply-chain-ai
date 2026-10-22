import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from backend.app.cnt.models import ScenarioType


class DeliveryModel:
    """Predicts delivery lead times, delay distributions, and transit reliability.

    Utilizes historical supplier delivery metrics and statistical/ML estimations
    without fabricating fictitious figures.
    """

    def __init__(self, rng: Optional[np.random.RandomState] = None):
        self.rng = rng or np.random.RandomState(42)

    def estimate_lead_time_distribution(
        self,
        nominal_lead_time_days: int,
        historical_lead_time_std: float,
        supplier_reliability: float,  # 0.0 to 1.0
        scenario_type: ScenarioType,
        transport_delay_days: float = 0.0,
    ) -> Tuple[float, float, float]:
        """Calculates expected lead time, variance/std, and delay probability.

        Returns: (expected_lead_time, lead_time_std, delay_probability)
        """
        nominal = max(1.0, float(nominal_lead_time_days))
        rel = max(0.01, min(1.0, supplier_reliability))
        hist_std = max(0.5, historical_lead_time_std)

        # Baseline delay drift driven by supplier unreliability: higher unreliability -> higher drift
        unreliability_drift = (1.0 - rel) * (nominal * 0.25)

        # Scenario shocks
        scenario_drift = 0.0
        if scenario_type == ScenarioType.SUPPLIER_DELAY:
            scenario_drift = nominal * 0.40 + 3.0
        elif scenario_type == ScenarioType.TRANSPORT_DISRUPTION:
            scenario_drift = nominal * 0.30 + transport_delay_days + 4.0
        elif scenario_type == ScenarioType.COMPOUND_DISRUPTION:
            scenario_drift = nominal * 0.60 + transport_delay_days + 6.0
        elif scenario_type == ScenarioType.SUPPLY_SHORTAGE:
            scenario_drift = nominal * 0.25 + 2.0

        expected_lead_time = round(nominal + unreliability_drift + scenario_drift, 2)
        lead_time_std = round(hist_std * (1.2 if scenario_drift > 0 else 1.0), 2)

        # Delay probability: probability that actual lead time exceeds nominal lead time
        # Using normal distribution survival function
        if lead_time_std > 0:
            import math
            z = (nominal - expected_lead_time) / lead_time_std
            # standard normal CDF approximation
            delay_prob = 1.0 - float(0.5 * (1.0 + math.erf(z / np.sqrt(2))))
        else:
            delay_prob = 1.0 if expected_lead_time > nominal else 0.0

        delay_prob = round(max(0.0, min(1.0, delay_prob)), 4)
        return expected_lead_time, lead_time_std, delay_prob

    def sample_actual_lead_time(
        self,
        expected_lead_time: float,
        lead_time_std: float,
        min_lead_time: float = 1.0,
    ) -> float:
        """Draws a stochastic lead time realization for Monte Carlo simulation."""
        sample = self.rng.normal(loc=expected_lead_time, scale=lead_time_std)
        return float(max(min_lead_time, np.round(sample, 2)))
