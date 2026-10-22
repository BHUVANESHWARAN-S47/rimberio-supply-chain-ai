from typing import List, Tuple
from backend.app.cnt.models import RiskLevel, ScenarioType


class RiskModel:
    """Multi-factor empirical risk assessment engine."""

    def evaluate_risk(
        self,
        supplier_reliability: float,  # 0.0 to 1.0
        lead_time_cv: float,          # std / mean lead time
        defect_rate: float,           # 0.0 to 1.0
        order_quantity: int,
        supplier_capacity: int,
        days_of_supply: float,
        target_days_of_supply: float,
        scenario_type: ScenarioType,
        disruption_history_events_count: int = 0,
        demand_cv: float = 0.20,
    ) -> Tuple[float, RiskLevel, float, List[str]]:
        """Calculates normalized risk score (0-100), risk level, confidence, and factors."""
        factors: List[str] = []

        # 1. Supplier Unreliability Risk (Weight 25)
        rel = max(0.0, min(1.0, supplier_reliability))
        rel_risk = (1.0 - rel) * 25.0
        if rel < 0.85:
            factors.append(f"Supplier historical reliability is suboptimal ({rel*100:.1f}%).")

        # 2. Lead Time Volatility Risk (Weight 15)
        lt_risk = min(15.0, lead_time_cv * 30.0)
        if lead_time_cv > 0.30:
            factors.append(f"High fulfillment lead-time variance (CV={lead_time_cv:.2f}).")

        # 3. Quality / Defect Risk (Weight 15)
        def_risk = min(15.0, defect_rate * 150.0)
        if defect_rate > 0.05:
            factors.append(f"Elevated component defect probability ({defect_rate*100:.2f}%).")

        # 4. Capacity Stress Risk (Weight 15)
        cap = max(1, supplier_capacity)
        cap_util = order_quantity / cap
        cap_risk = min(15.0, max(0.0, (cap_util - 0.70) * 50.0))
        if cap_util > 0.85:
            factors.append(f"Order consumes {cap_util*100:.1f}% of supplier monthly capacity.")

        # 5. Inventory Exposure Risk (Weight 15)
        target_dos = max(5.0, target_days_of_supply)
        if days_of_supply < target_dos:
            inv_risk = min(15.0, ((target_dos - days_of_supply) / target_dos) * 15.0)
            if days_of_supply < target_dos * 0.5:
                factors.append(f"Dangerous buffer depletion: {days_of_supply:.1f} days of supply.")
        else:
            inv_risk = 0.0

        # 6. Disruption and Scenario Stress (Weight 15)
        scenario_shock = 0.0
        if scenario_type in [ScenarioType.TRANSPORT_DISRUPTION, ScenarioType.SUPPLIER_DELAY]:
            scenario_shock = 8.0
            factors.append(f"Exogenous transit/supplier delay active in scenario ({scenario_type.value}).")
        elif scenario_type in [ScenarioType.INVENTORY_SHORTAGE, ScenarioType.SUPPLY_SHORTAGE]:
            scenario_shock = 10.0
            factors.append(f"Critical inventory/supply shortage condition simulated.")
        elif scenario_type == ScenarioType.COMPOUND_DISRUPTION:
            scenario_shock = 14.0
            factors.append(f"Multi-vector compound supply shock applied.")

        hist_risk = min(5.0, disruption_history_events_count * 1.5)
        if disruption_history_events_count > 0:
            factors.append(f"Supplier has {disruption_history_events_count} past logged risk incidents.")

        total_risk_score = round(
            min(100.0, max(5.0, rel_risk + lt_risk + def_risk + cap_risk + inv_risk + scenario_shock + hist_risk)),
            1,
        )

        if total_risk_score < 25.0:
            risk_level = RiskLevel.LOW
        elif total_risk_score < 50.0:
            risk_level = RiskLevel.MEDIUM
        elif total_risk_score < 75.0:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL

        # Confidence: higher when historical reliability is known and volatility is low
        confidence = round(max(0.60, min(0.98, 0.95 - (lead_time_cv * 0.3) - (defect_rate * 0.5))), 2)

        return total_risk_score, risk_level, confidence, factors
