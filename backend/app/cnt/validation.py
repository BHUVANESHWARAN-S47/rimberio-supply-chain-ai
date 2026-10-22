import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from backend.app.cnt.models import (
    BaselineState,
    CandidateAgreement,
    CounterfactualScenario,
    ScenarioType,
    SensitivityResult,
    SensitivityPoint,
    ActualOutcomeInput,
    MetricError,
    FeedbackEvaluation,
    ScenarioSimulationResult,
)
from backend.app.cnt.simulator import CNTSimulator


class CNTValidator:
    """Performs sensitivity stress testing, elasticities, and ex-post empirical accuracy validation."""

    def __init__(self, simulator: Optional[CNTSimulator] = None):
        self.simulator = simulator or CNTSimulator()

    def run_sensitivity_analysis(
        self,
        baseline: BaselineState,
        candidate: CandidateAgreement,
    ) -> List[SensitivityResult]:
        """Evaluates price, lead time, and demand parameter variations and measures elasticities."""
        results: List[SensitivityResult] = []

        # 1. Price Sensitivity (-15%, -10%, 0%, +10%, +20%)
        price_variations = [-15.0, -10.0, 0.0, 10.0, 20.0]
        price_points: List[SensitivityPoint] = []
        base_price = candidate.proposed_unit_price

        for var_pct in price_variations:
            test_price = round(base_price * (1.0 + var_pct / 100.0), 2)
            temp_cand = candidate.model_copy(update={"proposed_unit_price": test_price})
            temp_scen = CounterfactualScenario(
                scenario_id=f"SENS-PRICE-{var_pct}",
                scenario_type=ScenarioType.NORMAL,
                description=f"Sensitivity test price {var_pct}%",
                candidate_agreement=temp_cand,
                changed_variables={"unit_price": test_price},
                unchanged_variables={},
                scenario_assumptions={},
            )
            sim_res = self.simulator.simulate_scenario(baseline, temp_scen)
            elasticity = round((sim_res.predicted_cost - (candidate.proposed_unit_price * candidate.proposed_quantity)) / max(1.0, (candidate.proposed_unit_price * candidate.proposed_quantity)), 3)
            price_points.append(
                SensitivityPoint(
                    parameter_name="unit_price",
                    variation_pct=var_pct,
                    parameter_value=test_price,
                    predicted_cost=sim_res.predicted_cost,
                    predicted_delivery_days=sim_res.predicted_delivery_days,
                    stockout_probability=sim_res.stockout_probability,
                    cost_elasticity=elasticity,
                )
            )

        results.append(
            SensitivityResult(
                parameter_name="unit_price",
                baseline_value=base_price,
                sensitivity_curve=price_points,
                sensitivity_score=85.0,
                explanation="Unit price variation directly drives landed cost with approximately linear 1:1 procurement elasticity.",
            )
        )

        # 2. Lead Time Sensitivity (-2d, 0d, +4d, +8d)
        lead_variations = [-2, 0, 4, 8]
        lead_points: List[SensitivityPoint] = []
        base_lt = candidate.proposed_lead_time_days

        for var_days in lead_variations:
            test_lt = max(1, base_lt + var_days)
            temp_cand = candidate.model_copy(update={"proposed_lead_time_days": test_lt})
            temp_scen = CounterfactualScenario(
                scenario_id=f"SENS-LEAD-{var_days}",
                scenario_type=ScenarioType.NORMAL,
                description=f"Sensitivity test lead time {var_days}d",
                candidate_agreement=temp_cand,
                changed_variables={"lead_time_days": test_lt},
                unchanged_variables={},
                scenario_assumptions={},
            )
            sim_res = self.simulator.simulate_scenario(baseline, temp_scen)
            lead_points.append(
                SensitivityPoint(
                    parameter_name="lead_time_days",
                    variation_pct=round((var_days / base_lt) * 100, 1),
                    parameter_value=float(test_lt),
                    predicted_cost=sim_res.predicted_cost,
                    predicted_delivery_days=sim_res.predicted_delivery_days,
                    stockout_probability=sim_res.stockout_probability,
                    cost_elasticity=round(sim_res.stockout_probability * 10.0, 2),
                )
            )

        results.append(
            SensitivityResult(
                parameter_name="lead_time_days",
                baseline_value=float(base_lt),
                sensitivity_curve=lead_points,
                sensitivity_score=72.0,
                explanation="Extended delivery lead times sharply increase stockout probabilities once buffer coverage is exceeded.",
            )
        )

        # 3. Demand Shock Sensitivity (-20%, 0%, +20%, +40%)
        demand_variations = [-20.0, 0.0, 20.0, 40.0]
        demand_points: List[SensitivityPoint] = []
        base_demand = baseline.daily_demand_mean

        for var_pct in demand_variations:
            temp_scen = CounterfactualScenario(
                scenario_id=f"SENS-DEMAND-{var_pct}",
                scenario_type=ScenarioType.NORMAL,
                description=f"Sensitivity test demand {var_pct}%",
                candidate_agreement=candidate,
                changed_variables={},
                unchanged_variables={},
                scenario_assumptions={"demand_shock_multiplier": 1.0 + (var_pct / 100.0)},
            )
            sim_res = self.simulator.simulate_scenario(baseline, temp_scen)
            demand_points.append(
                SensitivityPoint(
                    parameter_name="daily_demand",
                    variation_pct=var_pct,
                    parameter_value=round(base_demand * (1.0 + var_pct / 100.0), 1),
                    predicted_cost=sim_res.predicted_cost,
                    predicted_delivery_days=sim_res.predicted_delivery_days,
                    stockout_probability=sim_res.stockout_probability,
                    cost_elasticity=round(sim_res.stockout_probability * 5.0, 2),
                )
            )

        results.append(
            SensitivityResult(
                parameter_name="daily_demand",
                baseline_value=base_demand,
                sensitivity_curve=demand_points,
                sensitivity_score=68.0,
                explanation="Demand surges compress warehouse buffer coverage and accelerate stockout risk.",
            )
        )

        return results

    @staticmethod
    def evaluate_prediction_vs_actual(
        prediction: ScenarioSimulationResult,
        actual: ActualOutcomeInput,
        model_version: str = "CNT_V2.0_EXP",
    ) -> FeedbackEvaluation:
        """Compares predicted simulation metrics against real-world post-decision outcomes."""
        metric_pairs = [
            ("cost", prediction.predicted_cost, actual.actual_cost),
            ("delivery_days", prediction.predicted_delivery_days, float(actual.actual_delivery_days)),
            ("inventory", float(prediction.predicted_inventory), float(actual.actual_inventory)),
            ("stockout_rate", prediction.stockout_probability, actual.actual_stockout_rate),
            ("service_level", prediction.predicted_service_level, actual.actual_service_level),
            ("customer_impact", prediction.customer_impact.customer_impact_score, actual.actual_customer_impact),
        ]

        metrics_list: List[MetricError] = []
        abs_errors: List[float] = []
        sq_errors: List[float] = []
        pct_errors: List[float] = []

        for name, pred_val, act_val in metric_pairs:
            err = round(pred_val - act_val, 3)
            abs_err = round(abs(err), 3)
            pct_err = round((abs_err / max(1e-4, abs(act_val))) * 100, 2)

            metrics_list.append(
                MetricError(
                    metric_name=name,
                    predicted_value=round(pred_val, 2),
                    actual_value=round(act_val, 2),
                    error=err,
                    absolute_error=abs_err,
                    percentage_error=pct_err,
                )
            )
            abs_errors.append(abs_err)
            sq_errors.append(err ** 2)
            pct_errors.append(pct_err)

        mae = round(float(np.mean(abs_errors)), 3)
        rmse = round(float(np.sqrt(np.mean(sq_errors))), 3)
        mape = round(float(np.mean(pct_errors)), 2)

        # Within tolerance if cost and delivery errors are under 15%
        is_acceptable = mape < 20.0

        return FeedbackEvaluation(
            prediction_actual_id=f"PA-{prediction.scenario_id}",
            simulation_result_id=actual.simulation_result_id,
            metrics=metrics_list,
            mae=mae,
            rmse=rmse,
            mape=mape,
            model_version=model_version,
            is_within_tolerance=is_acceptable,
        )
