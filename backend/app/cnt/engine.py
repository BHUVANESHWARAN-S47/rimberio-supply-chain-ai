import uuid
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy.orm import Session
from backend.app.database.connection import SessionLocal
from backend.app.database.models import (
    SupplierDB,
    ProductDB,
    SimulationRunDB,
    SimulationScenarioDB,
    SimulationResultDB,
    SupplierComparisonDB,
    CustomerImpactDB,
    PredictionActualDB,
    ModelFeedbackDB,
)
from backend.app.cnt.models import (
    BaselineState,
    CandidateAgreement,
    CounterfactualScenario,
    ScenarioType,
    SimulationConfig,
    ScenarioSimulationResult,
    ScenarioComparison,
    SensitivityResult,
    RankedCandidate,
    ActualOutcomeInput,
    FeedbackEvaluation,
    CNTSimulationRequest,
    CNTSimulationResponse,
    CostBreakdown,
    RiskLevel,
    ImpactLevel,
    CustomerImpactResult,
)
from backend.app.cnt.state_builder import StateBuilder
from backend.app.cnt.baseline import BaselineManager
from backend.app.cnt.scenarios import ScenarioGenerator
from backend.app.cnt.simulator import CNTSimulator
from backend.app.cnt.comparison import ScenarioComparator
from backend.app.cnt.validation import CNTValidator
from backend.app.cnt.explain import CNTExplainer
from backend.app.cnt.uncertainty import UncertaintyEngine


class CNTEngine:
    """Counterfactual Negotiation Twin (CNT) Core Innovation Engine.

    Data-driven simulation, causal inference, and multi-objective alternative evaluation
    platform for adaptive supply chain decisions.
    """

    _global_cache: Dict[str, Any] = {}

    def __init__(self, db: Optional[Session] = None):

        self.db = db
        self.state_builder = StateBuilder(db=db)
        self.baseline_manager = BaselineManager(state_builder=self.state_builder)
        self._cache: Dict[str, Any] = {}

    def simulate(
        self,
        request: CNTSimulationRequest,
    ) -> CNTSimulationResponse:
        """Executes full CNT pipeline: state retrieval, counterfactual generation, Monte Carlo simulation, comparison, and persistence."""
        start_time = time.perf_counter()
        config = request.config or SimulationConfig()

        # 1. Retrieve Current Supply Chain State & Build Baseline
        baseline = self.baseline_manager.create_baseline(
            product_id=request.product_id,
            supplier_id=request.supplier_id,
            order_quantity=request.order_quantity,
            decision_timestamp=config.decision_timestamp,
        )

        # 2. Identify Candidate Agreements (Incumbent + User Provided / Auto-resolved)
        candidate_agreements: List[CandidateAgreement] = []
        incumbent_candidate = self.baseline_manager.baseline_to_candidate_agreement(baseline)
        candidate_agreements.append(incumbent_candidate)

        if request.candidate_agreements:
            for cand in request.candidate_agreements:
                if cand.supplier_id != incumbent_candidate.supplier_id:
                    candidate_agreements.append(cand)
        else:
            # Auto-resolve alternative suppliers from PostgreSQL if not provided
            candidate_agreements.extend(self._resolve_alternative_suppliers(baseline))

        # 3. Generate Counterfactual Scenarios
        scenarios = ScenarioGenerator.generate_scenarios(
            baseline=baseline,
            candidate_agreements=candidate_agreements,
            scenario_types=request.scenarios_to_generate,
        )

        # 4. In-Memory Customer Orders Detail for Impact Modeling
        cutoff = config.decision_timestamp or datetime.utcnow()
        pending_orders = self.state_builder.get_pending_customer_orders_detail(
            product_id=baseline.product_id,
            cutoff=cutoff,
        )

        # 5. Simulate Scenarios across Monte Carlo Engine
        simulator = CNTSimulator(config=config)
        simulation_results: List[ScenarioSimulationResult] = []

        # Find or simulate baseline scenario first
        baseline_scen = next(
            (s for s in scenarios if s.candidate_agreement.is_incumbent and s.scenario_type == ScenarioType.NORMAL),
            scenarios[0],
        )
        baseline_res = simulator.simulate_scenario(baseline, baseline_scen, pending_orders)
        simulation_results.append(baseline_res)

        for sc in scenarios:
            if sc.scenario_id == baseline_scen.scenario_id:
                continue
            res = simulator.simulate_scenario(baseline, sc, pending_orders)
            simulation_results.append(res)

        # 6. Scenario Comparison, Pareto Frontier, and Multi-Objective Ranking
        comparator = ScenarioComparator(weights=config.weights)
        comparison = comparator.compare_scenarios(
            baseline_result=baseline_res,
            candidate_results=simulation_results,
        )

        # 7. Sensitivity Analysis on Top Candidate
        top_cand_agreement = (
            next((c for c in candidate_agreements if c.supplier_id == comparison.rankings[0].supplier_id), incumbent_candidate)
            if comparison.rankings
            else incumbent_candidate
        )
        validator = CNTValidator(simulator=simulator)
        sensitivities = validator.run_sensitivity_analysis(baseline, top_cand_agreement)

        # 8. Causal Explanations
        explanation = CNTExplainer.generate_explanation(baseline, comparison, sensitivities)

        # 9. Persistence to Relational Database
        run_id = f"RUN-{uuid.uuid4().hex[:12].upper()}"
        self._persist_simulation(
            run_id=run_id,
            baseline=baseline,
            scenarios=scenarios,
            simulation_results=simulation_results,
            comparison=comparison,
            config=config,
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        reproducibility_hash = hashlib.sha256(
            f"{run_id}_{config.random_seed}_{config.model_version}".encode("utf-8")
        ).hexdigest()[:16]

        response = CNTSimulationResponse(
            simulation_id=run_id,
            baseline=baseline,
            scenarios=simulation_results,
            comparison=comparison,
            sensitivity=sensitivities,
            recommendation_candidates=comparison.rankings,
            explanation=explanation,
            execution_time_ms=elapsed_ms,
            model_version=config.model_version,
            reproducibility_hash=reproducibility_hash,
        )

        # Cache in memory for quick API lookups
        self._cache[run_id] = response
        CNTEngine._global_cache[run_id] = response
        return response

    def get_simulation(self, run_id: str) -> Optional[CNTSimulationResponse]:
        """Retrieves simulation response from memory cache or database."""
        if run_id in self._cache:
            return self._cache[run_id]
        if run_id in CNTEngine._global_cache:
            return CNTEngine._global_cache[run_id]
        return None


    def record_actual_outcome(self, outcome: ActualOutcomeInput) -> FeedbackEvaluation:
        """Stores actual decision execution outcomes and computes prediction performance errors."""
        db = self.db or SessionLocal()
        try:
            # Query simulation result
            res_db = (
                db.query(SimulationResultDB)
                .filter(SimulationResultDB.id == outcome.simulation_result_id)
                .first()
            )

            pred_cost = res_db.predicted_cost if res_db else outcome.actual_cost * 1.05
            pred_lead = res_db.predicted_delivery_delay if res_db else outcome.actual_delivery_days
            pred_inv = res_db.predicted_inventory if res_db else outcome.actual_inventory
            pred_stockout = res_db.predicted_stockout_rate if res_db else outcome.actual_stockout_rate
            pred_service = res_db.predicted_service_level if res_db else outcome.actual_service_level
            pred_impact = res_db.predicted_customer_impact if res_db else outcome.actual_customer_impact

            # Store PredictionActualDB
            actual_record = PredictionActualDB(
                simulation_result_id=res_db.id if res_db else uuid.uuid4(),
                actual_supplier_id=uuid.UUID(outcome.actual_supplier_id) if len(outcome.actual_supplier_id) == 36 else uuid.uuid4(),
                actual_cost=outcome.actual_cost,
                actual_delivery_days=outcome.actual_delivery_days,
                actual_inventory=outcome.actual_inventory,
                actual_stockout_rate=outcome.actual_stockout_rate,
                actual_service_level=outcome.actual_service_level,
                actual_customer_impact=outcome.actual_customer_impact,
                recorded_at=outcome.recorded_at or datetime.utcnow(),
            )
            db.add(actual_record)
            db.flush()

            # Record feedback metrics
            pairs = [
                ("cost", pred_cost, outcome.actual_cost),
                ("delivery_days", float(pred_lead), float(outcome.actual_delivery_days)),
                ("inventory", float(pred_inv), float(outcome.actual_inventory)),
                ("stockout_rate", float(pred_stockout), float(outcome.actual_stockout_rate)),
                ("service_level", float(pred_service), float(outcome.actual_service_level)),
                ("customer_impact", float(pred_impact), float(outcome.actual_customer_impact)),
            ]

            feedback_entries = []
            for name, p_val, a_val in pairs:
                err = round(p_val - a_val, 3)
                abs_err = round(abs(err), 3)
                pct_err = round((abs_err / max(1e-4, abs(a_val))) * 100, 2)
                fb = ModelFeedbackDB(
                    prediction_actual_id=actual_record.id,
                    metric_name=name,
                    predicted_value=round(p_val, 2),
                    actual_value=round(a_val, 2),
                    error=err,
                    absolute_error=abs_err,
                    percentage_error=pct_err,
                )
                db.add(fb)
                feedback_entries.append(fb)

            db.commit()

            # Return Evaluation
            temp_res = ScenarioSimulationResult(
                scenario_id="ACTUAL-EVAL",
                scenario_type=ScenarioType.NORMAL,
                candidate_supplier_id=outcome.actual_supplier_id,
                candidate_supplier_name="Actual Evaluated Supplier",
                predicted_cost=pred_cost,
                cost_range=UncertaintyEngine.aggregate_distribution(np.array([pred_cost])),
                cost_breakdown=CostBreakdown(
                    purchase_cost=pred_cost,
                    transportation_cost=0.0,
                    holding_cost=0.0,
                    stockout_cost=0.0,
                    quality_failure_cost=0.0,
                    delay_cost=0.0,
                    switching_cost=0.0,
                    expediting_cost=0.0,
                    total_landed_cost=pred_cost,
                ),
                predicted_delivery_days=float(pred_lead),
                delivery_range=UncertaintyEngine.aggregate_distribution(np.array([float(pred_lead)])),
                predicted_delivery_delay=0.0,
                stockout_probability=float(pred_stockout),
                stockout_quantity_expected=0.0,
                predicted_inventory=int(pred_inv),
                predicted_risk=20.0,
                risk_level=RiskLevel.LOW,
                risk_factors=[],
                predicted_service_level=float(pred_service),
                customer_impact=CustomerImpactResult(
                    affected_customers=[],
                    affected_orders=[],
                    expected_delay_days=0.0,
                    service_level_change=0.0,
                    revenue_at_risk=0.0,
                    customer_impact_score=float(pred_impact),
                    impact_level=ImpactLevel.LOW,
                    reasoning="Recorded actual evaluation baseline.",
                ),
                confidence=0.92,
                changed_variables={},
                unchanged_variables={},
                scenario_assumptions={},
            )

            return CNTValidator.evaluate_prediction_vs_actual(temp_res, outcome)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            if not self.db:
                db.close()

    def _resolve_alternative_suppliers(self, baseline: BaselineState) -> List[CandidateAgreement]:
        """Queries alternative suppliers from PostgreSQL."""
        db = self.db or SessionLocal()
        candidates: List[CandidateAgreement] = []
        try:
            suppliers = (
                db.query(SupplierDB)
                .filter(SupplierDB.supplier_code != baseline.supplier_code)
                .limit(3)
                .all()
            )
            for s in suppliers:
                candidates.append(
                    CandidateAgreement(
                        supplier_id=str(s.id),
                        supplier_code=s.supplier_code,
                        company_name=s.company_name,
                        proposed_unit_price=round(baseline.current_unit_price * 0.94, 2),
                        proposed_quantity=baseline.current_quantity,
                        proposed_lead_time_days=baseline.current_lead_time_days + 3,
                        proposed_quality_score=92.0,
                        payment_terms="Net 30",
                        transport_cost=round(baseline.current_quantity * 1.8, 2),
                        is_incumbent=False,
                    )
                )
        except Exception:
            pass
        finally:
            if not self.db:
                db.close()
        return candidates

    def _persist_simulation(
        self,
        run_id: str,
        baseline: BaselineState,
        scenarios: List[CounterfactualScenario],
        simulation_results: List[ScenarioSimulationResult],
        comparison: ScenarioComparison,
        config: SimulationConfig,
    ) -> None:
        """Stores simulation run, scenarios, results, and comparisons into database."""
        db = self.db or SessionLocal()
        try:
            sup_uuid = uuid.UUID(baseline.supplier_id) if len(baseline.supplier_id) == 36 else None
            prod_uuid = uuid.UUID(baseline.product_id) if len(baseline.product_id) == 36 else None

            sim_run = SimulationRunDB(
                run_id=run_id,
                trigger_type="MANUAL_EVALUATION",
                supplier_id=sup_uuid,
                product_id=prod_uuid,
                baseline_reference=baseline.snapshot_id,
                created_by="CNT_TWIN_ENGINE",
                status="COMPLETED",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )
            db.add(sim_run)
            db.flush()

            # Store Scenarios & Results
            for sc in scenarios:
                sc_db = SimulationScenarioDB(
                    simulation_run_id=sim_run.id,
                    scenario_type=sc.scenario_type.value,
                    description=sc.description,
                    assumptions=sc.scenario_assumptions,
                )
                db.add(sc_db)
                db.flush()

                # Find matching result
                res = next((r for r in simulation_results if r.scenario_id == sc.scenario_id), None)
                if res:
                    c_sup_id = uuid.UUID(res.candidate_supplier_id) if len(res.candidate_supplier_id) == 36 else sup_uuid or uuid.uuid4()
                    res_db = SimulationResultDB(
                        simulation_scenario_id=sc_db.id,
                        candidate_supplier_id=c_sup_id,
                        candidate_price=sc.candidate_agreement.proposed_unit_price,
                        candidate_delivery_days=sc.candidate_agreement.proposed_lead_time_days,
                        predicted_cost=res.predicted_cost,
                        predicted_profit=round(res.predicted_cost * 0.15, 2),
                        predicted_inventory=res.predicted_inventory,
                        predicted_delivery_delay=res.predicted_delivery_delay,
                        predicted_stockout_rate=res.stockout_probability,
                        predicted_risk=res.predicted_risk,
                        predicted_service_level=res.predicted_service_level,
                        predicted_customer_impact=res.customer_impact.customer_impact_score,
                        prediction_confidence=res.confidence,
                        model_version=config.model_version,
                    )
                    db.add(res_db)

            # Store Comparisons
            for rk in comparison.rankings:
                rk_sup_id = uuid.UUID(rk.supplier_id) if len(rk.supplier_id) == 36 else sup_uuid or uuid.uuid4()
                comp_db = SupplierComparisonDB(
                    simulation_run_id=sim_run.id,
                    supplier_id=rk_sup_id,
                    price_score=rk.price_score,
                    quality_score=rk.quality_score,
                    delivery_score=rk.delivery_score,
                    reliability_score=rk.reliability_score,
                    risk_score=rk.risk_score,
                    logistics_score=85.0,
                    customer_impact_score=rk.service_score,
                    overall_score=rk.overall_score,
                    rank=rk.rank,
                    explanation=rk.recommendation_rationale,
                )
                db.add(comp_db)

            db.commit()
        except Exception:
            db.rollback()
        finally:
            if not self.db:
                db.close()
