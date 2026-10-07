import numpy as np
from typing import Dict, Any, List

class LogisticsAgentModel:
    """
    Logistics Agent Model for Global Maritime, Air & Ground Telemetry.
    Estimates transit delay, port congestion variance, and landed freight surcharges
    for ANY arbitrary route, carrier, and disruption scenario.
    """

    CHOKEPOINTS = {
        "Suez Canal": {"base_delay": 5.5, "cost_multiplier": 1.25, "risk_factor": 0.45},
        "Panama Canal": {"base_delay": 7.0, "cost_multiplier": 1.30, "risk_factor": 0.40},
        "Strait of Malacca": {"base_delay": 2.0, "cost_multiplier": 1.08, "risk_factor": 0.15},
        "Rotterdam Terminal": {"base_delay": 3.5, "cost_multiplier": 1.12, "risk_factor": 0.25},
        "LA Long Beach": {"base_delay": 4.0, "cost_multiplier": 1.15, "risk_factor": 0.28},
    }

    def predict_route_transit(
        self,
        origin_port: str,
        destination_port: str,
        base_transit_days: int,
        chokepoints_crossed: List[str],
        weather_severity_index: float = 0.0,  # 0.0 to 1.0
        fuel_surcharge_rate: float = 0.05
    ) -> Dict[str, Any]:
        """
        Calculates predicted transit days and cost deltas on ANY maritime/freight route.
        """
        chokepoint_delay = 0.0
        freight_multiplier = 1.0 + fuel_surcharge_rate
        composite_risk = 0.0

        for cp in chokepoints_crossed:
            info = self.CHOKEPOINTS.get(cp, {"base_delay": 2.0, "cost_multiplier": 1.05, "risk_factor": 0.10})
            chokepoint_delay += info["base_delay"]
            freight_multiplier *= info["cost_multiplier"]
            composite_risk = max(composite_risk, info["risk_factor"])

        weather_delay = weather_severity_index * 4.0
        total_delay_days = chokepoint_delay + weather_delay
        expected_transit_days = base_transit_days + total_delay_days

        # Variance estimation (e.g. queueing model standard deviation)
        variance_days = np.sqrt(total_delay_days + 1.0) * 1.2

        corridor_status = "CRITICAL_CONGESTION" if total_delay_days > 6.0 else ("DELAYED" if total_delay_days > 2.0 else "NOMINAL")

        return {
            "origin_port": origin_port,
            "destination_port": destination_port,
            "base_transit_days": base_transit_days,
            "predicted_transit_days": round(float(expected_transit_days), 1),
            "delay_days_delta": round(float(total_delay_days), 1),
            "transit_variance_days": round(float(variance_days), 2),
            "freight_cost_surge_percent": round(float((freight_multiplier - 1.0) * 100.0), 1),
            "corridor_status": corridor_status,
            "recommended_buffer_days": int(np.ceil(expected_transit_days + (1.96 * variance_days))),
            "advisory": (
                f"Logistics Telemetry: Route {origin_port} -> {destination_port} exhibits "
                f"+{total_delay_days:.1f} days congestion delay across {len(chokepoints_crossed)} chokepoint(s). "
                f"Buffer corridor recommended: {int(np.ceil(expected_transit_days + 1.96 * variance_days))} days."
            )
        }
