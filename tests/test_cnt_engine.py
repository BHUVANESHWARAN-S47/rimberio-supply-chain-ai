import pytest
import numpy as np
from datetime import datetime, timedelta
from pydantic import ValidationError

from backend.app.cnt.models import (
    ScenarioType,
    RiskLevel,
    ImpactLevel,
    CostAssumptions,
    MultiObjectiveWeights,
    SimulationConfig,
    CandidateAgreement,
    BaselineState,
    CounterfactualScenario,
    CostBreakdown,
    UncertaintyRange,
    CustomerImpactResult,
    ScenarioSimulationResult,
    ComparisonMetricDelta,
    RankedCandidate,
    ScenarioComparison,
    SensitivityPoint,
    SensitivityResult,
    ActualOutcomeInput,
    MetricError,
    FeedbackEvaluation,
    CNTSimulationRequest,
    CNTSimulationResponse,
)
from backend.app.cnt.cost_model import CostModel
from backend.app.cnt.demand_model import DemandModel
from backend.app.cnt.delivery_model import DeliveryModel
from backend.app.cnt.quality_model import QualityModel
from backend.app.cnt.inventory_model import InventoryModel
from backend.app.cnt.risk_model import RiskModel
from backend.app.cnt.customer_model import CustomerImpactModel
from backend.app.cnt.uncertainty import UncertaintyEngine
from backend.app.cnt.state_builder import StateBuilder
from backend.app.cnt.baseline import BaselineManager
from backend.app.cnt.scenarios import ScenarioGenerator
from backend.app.cnt.simulator import CNTSimulator
from backend.app.cnt.comparison import ScenarioComparator
from backend.app.cnt.validation import CNTValidator
from backend.app.cnt.explain import CNTExplainer
from backend.app.cnt.engine import CNTEngine
from backend.app.cnt.ablation import AblationStudyRunner

from backend.app.database.connection import SessionLocal
from backend.app.database.models import (
    ProductDB,
    SupplierDB,
    SupplierProductDB,
    SimulationRunDB,
)


@pytest.fixture
def sample_baseline():
    return BaselineState(
        snapshot_id="SNAP-TEST-001",
        snapshot_hash="a1b2c3d4e5f60001",
        timestamp=datetime.utcnow(),
        product_id="PROD-TEST-777",
        product_sku="SKU-MICRO-01",
        product_name="Micro Controller Unit",
        supplier_id="SUP-INCUMBENT-01",
        supplier_code="ALPHA-SEMI",
        supplier_name="Alpha Semiconductor Corp",
        current_unit_price=100.0,
        current_lead_time_days=10,
        current_quantity=1000,
        current_inventory=3000,
        safety_stock=800,
        reorder_point=1500,
        daily_demand_mean=50.0,
        daily_demand_std=10.0,
        forecast_demand_30d=1500.0,
        supplier_historical_reliability=0.95,
        supplier_historical_defect_rate=0.015,
        supplier_lead_time_std=1.5,
        supplier_capacity=50000,
        pending_customer_orders_count=12,
        total_customer_order_units=600,
        active_shipments_count=2,
        current_service_level=98.0,
        current_risk_score=15.0,
        data_cutoff_timestamp=datetime.utcnow(),
    )


@pytest.fixture
def alternative_candidate():
    return CandidateAgreement(
        supplier_id="SUP-ALTERNATIVE-02",
        supplier_code="BETA-TECH",
        company_name="Beta Technologies Ltd",
        proposed_unit_price=92.0,
        proposed_quantity=1000,
        proposed_lead_time_days=14,
        proposed_quality_score=91.0,
        proposed_capacity=45000,
        payment_terms="Net 45",
        transport_cost=1200.0,
        is_incumbent=False,
    )


# ==============================================================================
# 1. BASELINE REPRODUCTION & DATA INTEGRITY
# ==============================================================================

def test_01_baseline_snapshot_hash_reproducibility(sample_baseline):
    """Ensures baseline state snapshot hash and attributes are deterministic and immutable."""
    assert sample_baseline.snapshot_id.startswith("SNAP-")
    assert sample_baseline.current_unit_price == 100.0
    assert sample_baseline.daily_demand_mean == 50.0
    assert sample_baseline.supplier_historical_reliability == 0.95


def test_02_baseline_to_candidate_translation(sample_baseline):
    """Manager translates baseline into incumbent candidate agreement accurately."""
    mgr = BaselineManager()
    cand = mgr.baseline_to_candidate_agreement(sample_baseline)
    assert cand.is_incumbent is True
    assert cand.proposed_unit_price == 100.0
    assert cand.proposed_lead_time_days == 10
    assert cand.supplier_id == sample_baseline.supplier_id


# ==============================================================================
# 2. SCENARIO GENERATION & COUNTERFACTUAL INTEGRITY
# ==============================================================================

def test_03_generate_all_11_counterfactual_scenarios(sample_baseline, alternative_candidate):
    """Generates all 11 scenario types while strictly tracking changed vs unchanged variables."""
    all_types = list(ScenarioType)
    scenarios = ScenarioGenerator.generate_scenarios(
        baseline=sample_baseline,
        candidate_agreements=[alternative_candidate],
        scenario_types=all_types,
    )
    assert len(scenarios) == 11
    types_generated = {s.scenario_type for s in scenarios}
    assert types_generated == set(all_types)


def test_04_counterfactual_variable_isolation(sample_baseline, alternative_candidate):
    """Verifies that only intended candidate variables change, keeping baseline controlled."""
    scenarios = ScenarioGenerator.generate_scenarios(
        baseline=sample_baseline,
        candidate_agreements=[alternative_candidate],
        scenario_types=[ScenarioType.NORMAL],
    )
    sc = scenarios[0]
    # Changed variables must include supplier_id, unit_price, lead_time_days
    assert sc.changed_variables["supplier_id"] == "SUP-ALTERNATIVE-02"
    assert sc.changed_variables["unit_price"] == 92.0
    assert sc.changed_variables["lead_time_days"] == 14
    # Unchanged variables must preserve baseline context
    assert sc.unchanged_variables["current_inventory"] == sample_baseline.current_inventory
    assert sc.unchanged_variables["daily_demand_mean"] == sample_baseline.daily_demand_mean


# ==============================================================================
# 3. COST MODEL TESTING
# ==============================================================================

def test_05_cost_model_transparent_formula():
    """Validates transparent landed cost formula identity across all constituent costs."""
    cm = CostModel(CostAssumptions(
        holding_cost_annual_rate=0.20,
        stockout_cost_per_unit=25.0,
        delay_cost_per_day=100.0,
        quality_failure_multiplier=2.0,
        switching_fixed_cost=1000.0,
        expediting_fee_per_unit=10.0,
        time_horizon_days=30,
    ))
    cb = cm.calculate_cost(
        unit_price=50.0,
        quantity=1000,
        transport_cost=2000.0,
        average_inventory=1500.0,
        stockout_quantity=50.0,
        defect_rate=0.02,
        expected_lead_time_days=15.0,
        baseline_lead_time_days=10.0,
        is_supplier_switch=True,
        expedited_units=20.0,
    )
    # 1. purchase = 50 * 1000 = 50000
    assert cb.purchase_cost == 50000.0
    # 2. transport = 2000
    assert cb.transportation_cost == 2000.0
    # 3. holding = 1500 * 50 * 0.20 * (30/365) = 1232.88
    assert cb.holding_cost > 1200.0
    # 4. stockout = 50 * 25 = 1250.0
    assert cb.stockout_cost == 1250.0
    # 5. quality = (1000 * 0.02) * 50 * 2.0 = 2000.0
    assert cb.quality_failure_cost == 2000.0
    # 6. delay = (15 - 10) * 100 = 500.0
    assert cb.delay_cost == 500.0
    # 7. switching = 1000.0
    assert cb.switching_cost == 1000.0
    # 8. expediting = 20 * 10 = 200.0
    assert cb.expediting_cost == 200.0
    # 9. total = sum of all components
    expected_sum = (
        cb.purchase_cost + cb.transportation_cost + cb.holding_cost
        + cb.stockout_cost + cb.quality_failure_cost + cb.delay_cost
        + cb.switching_cost + cb.expediting_cost
    )
    assert round(cb.total_landed_cost, 2) == round(expected_sum, 2)


def test_06_cost_model_zero_switch_cost_for_incumbent():
    """Incumbent supplier incurs $0 switching cost."""
    cm = CostModel()
    cb = cm.calculate_cost(
        unit_price=100.0,
        quantity=500,
        transport_cost=500.0,
        average_inventory=500.0,
        stockout_quantity=0.0,
        defect_rate=0.0,
        expected_lead_time_days=10.0,
        baseline_lead_time_days=10.0,
        is_supplier_switch=False,
    )
    assert cb.switching_cost == 0.0
    assert cb.delay_cost == 0.0


# ==============================================================================
# 4. INVENTORY MODEL TESTING
# ==============================================================================

def test_07_inventory_physical_non_negative_conservation():
    """Ensures inventory never becomes negative regardless of catastrophic demand shocks."""
    im = InventoryModel()
    daily_demands = np.full(30, 200.0)  # Massive 200 units/day demand
    closing_inv, avg_inv, stockout_units, stockout_rate = im.simulate_inventory_trajectory(
        opening_inventory=500,          # Only 500 units on hand
        incoming_quantity=1000,
        daily_demands=daily_demands,
        actual_lead_time_days=20.0,     # Arrival on day 20
        safety_stock=200,
        scenario_type=ScenarioType.NORMAL,
    )
    # Inventory cannot be negative
    assert closing_inv >= 0
    assert avg_inv >= 0.0
    assert stockout_units > 0.0
    assert stockout_rate > 0.0


def test_08_inventory_no_stockout_with_sufficient_buffer():
    """When buffer exceeds lead time demand, stockout units and rate are strictly zero."""
    im = InventoryModel()
    daily_demands = np.full(30, 10.0)  # Low demand (10 units/day)
    closing_inv, avg_inv, stockout_units, stockout_rate = im.simulate_inventory_trajectory(
        opening_inventory=2000,
        incoming_quantity=500,
        daily_demands=daily_demands,
        actual_lead_time_days=5.0,
        safety_stock=500,
        scenario_type=ScenarioType.NORMAL,
    )
    assert stockout_units == 0.0
    assert stockout_rate == 0.0
    assert closing_inv > 1500


# ==============================================================================
# 5. DELIVERY & QUALITY MODEL TESTING
# ==============================================================================

def test_09_delivery_model_scenario_drift_estimation():
    """Supplier delay scenario increases expected lead time and delay probability."""
    dm = DeliveryModel(rng=np.random.RandomState(42))
    exp_lt_norm, _, prob_norm = dm.estimate_lead_time_distribution(
        nominal_lead_time_days=10,
        historical_lead_time_std=1.5,
        supplier_reliability=0.95,
        scenario_type=ScenarioType.NORMAL,
    )
    exp_lt_delay, _, prob_delay = dm.estimate_lead_time_distribution(
        nominal_lead_time_days=10,
        historical_lead_time_std=1.5,
        supplier_reliability=0.95,
        scenario_type=ScenarioType.SUPPLIER_DELAY,
    )
    assert exp_lt_delay > exp_lt_norm
    assert prob_delay > prob_norm


def test_10_quality_model_defect_rate_escalation():
    """Quality degradation scenario amplifies defect rates and costs."""
    qm = QualityModel(rng=np.random.RandomState(42))
    norm_rate, norm_defects, norm_cost = qm.estimate_quality_metrics(
        base_defect_rate=0.02,
        order_quantity=1000,
        unit_cost=100.0,
        scenario_type=ScenarioType.NORMAL,
    )
    deg_rate, deg_defects, deg_cost = qm.estimate_quality_metrics(
        base_defect_rate=0.02,
        order_quantity=1000,
        unit_cost=100.0,
        scenario_type=ScenarioType.QUALITY_DEGRADATION,
    )
    assert deg_rate > norm_rate
    assert deg_defects > norm_defects
    assert deg_cost > norm_cost


# ==============================================================================
# 6. RISK & CUSTOMER IMPACT TESTING
# ==============================================================================

def test_11_risk_model_bounded_score_and_factors():
    """Evaluates risk score between 0 and 100, assigns correct category, and produces audit factors."""
    rm = RiskModel()
    score, level, conf, factors = rm.evaluate_risk(
        supplier_reliability=0.70,   # poor reliability
        lead_time_cv=0.45,           # high volatility
        defect_rate=0.08,            # high defects
        order_quantity=45000,
        supplier_capacity=50000,     # high utilization
        days_of_supply=4.0,          # buffer crisis
        target_days_of_supply=20.0,
        scenario_type=ScenarioType.COMPOUND_DISRUPTION,
    )
    assert 0.0 <= score <= 100.0
    assert level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    assert len(factors) >= 3


def test_12_customer_impact_order_linking():
    """Downstream customer orders and revenue at risk are quantified when fulfillment is delayed."""
    cim = CustomerImpactModel()
    pending = [
        {"customer_id": "C-1", "customer_name": "Acme Corp", "order_id": "O-1", "order_number": "ORD-101", "total_amount": 25000.0, "quantity": 250},
        {"customer_id": "C-2", "customer_name": "Globex Inc", "order_id": "O-2", "order_number": "ORD-102", "total_amount": 15000.0, "quantity": 150},
    ]
    res = cim.evaluate_customer_impact(
        pending_orders=pending,
        stockout_rate=0.15,
        stockout_units=200.0,
        actual_lead_time_days=18.0,
        baseline_lead_time_days=10.0,
        unit_price=100.0,
    )
    assert len(res.affected_customers) == 2
    assert len(res.affected_orders) == 2
    assert res.revenue_at_risk == 40000.0
    assert res.service_level_change < 0.0
    assert res.customer_impact_score > 20.0


# ==============================================================================
# 7. MONTE CARLO & REPRODUCIBILITY TESTING
# ==============================================================================

def test_13_uncertainty_quantiles_ordering():
    """Verifies that P10 <= median <= P90 <= max for Monte Carlo distributions."""
    vals = np.array([10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0])
    u = UncertaintyEngine.aggregate_distribution(vals)
    assert u.min_val <= u.p10 <= u.median <= u.p90 <= u.max_val
    assert u.mean == 55.0


def test_14_monte_carlo_random_seed_reproducibility(sample_baseline, alternative_candidate):
    """Identical random seeds produce exact numerical reproductions across simulation runs."""
    cfg1 = SimulationConfig(num_monte_carlo_runs=100, random_seed=999)
    cfg2 = SimulationConfig(num_monte_carlo_runs=100, random_seed=999)

    sim1 = CNTSimulator(config=cfg1)
    sim2 = CNTSimulator(config=cfg2)

    scen = CounterfactualScenario(
        scenario_id="TEST-REPRO",
        scenario_type=ScenarioType.NORMAL,
        description="Reproducibility test",
        candidate_agreement=alternative_candidate,
        changed_variables={},
        unchanged_variables={},
        scenario_assumptions={},
    )

    res1 = sim1.simulate_scenario(sample_baseline, scen)
    res2 = sim2.simulate_scenario(sample_baseline, scen)

    assert res1.predicted_cost == res2.predicted_cost
    assert res1.cost_range.p10 == res2.cost_range.p10
    assert res1.cost_range.p90 == res2.cost_range.p90
    assert res1.predicted_delivery_days == res2.predicted_delivery_days


# ==============================================================================
# 8. PARETO & MULTI-OBJECTIVE COMPARISON
# ==============================================================================

def test_15_pareto_frontier_and_candidate_ranking(sample_baseline, alternative_candidate):
    """Detects Pareto-optimal non-dominated solutions and calculates ranked utility scores."""
    cfg = SimulationConfig(num_monte_carlo_runs=50, random_seed=42)
    sim = CNTSimulator(config=cfg)

    # Candidate 1: baseline
    cand_base = BaselineManager().baseline_to_candidate_agreement(sample_baseline)
    sc_base = CounterfactualScenario(
        scenario_id="SCEN-BASE",
        scenario_type=ScenarioType.NORMAL,
        description="Baseline incumbent",
        candidate_agreement=cand_base,
        changed_variables={},
        unchanged_variables={},
        scenario_assumptions={},
    )
    res_base = sim.simulate_scenario(sample_baseline, sc_base)

    # Candidate 2: cheaper alternative
    sc_alt = CounterfactualScenario(
        scenario_id="SCEN-ALT",
        scenario_type=ScenarioType.NORMAL,
        description="Alternative beta",
        candidate_agreement=alternative_candidate,
        changed_variables={},
        unchanged_variables={},
        scenario_assumptions={},
    )
    res_alt = sim.simulate_scenario(sample_baseline, sc_alt)

    comparator = ScenarioComparator()
    comp = comparator.compare_scenarios(res_base, [res_alt])

    assert len(comp.scenarios) == 2
    assert len(comp.pareto_frontier) >= 1
    assert len(comp.rankings) == 2
    assert comp.rankings[0].rank == 1
    assert comp.rankings[1].rank == 2


# ==============================================================================
# 9. SENSITIVITY & VALIDATION TESTING
# ==============================================================================

def test_16_sensitivity_analysis_curves(sample_baseline, alternative_candidate):
    """Produces multi-point sensitivity curves across price, lead time, and demand."""
    cfg = SimulationConfig(num_monte_carlo_runs=30, random_seed=42)
    val = CNTValidator(simulator=CNTSimulator(config=cfg))
    sens = val.run_sensitivity_analysis(sample_baseline, alternative_candidate)

    assert len(sens) == 3
    names = [s.parameter_name for s in sens]
    assert "unit_price" in names
    assert "lead_time_days" in names
    assert "daily_demand" in names

    # Price sensitivity curve must have 5 points
    price_sens = next(s for s in sens if s.parameter_name == "unit_price")
    assert len(price_sens.sensitivity_curve) == 5


def test_17_prediction_vs_actual_error_metrics(sample_baseline, alternative_candidate):
    """Computes MAE, RMSE, and percentage errors against recorded actual outcomes."""
    cfg = SimulationConfig(num_monte_carlo_runs=30, random_seed=42)
    sim = CNTSimulator(config=cfg)
    sc = CounterfactualScenario(
        scenario_id="SCEN-ACTUAL-TEST",
        scenario_type=ScenarioType.NORMAL,
        description="Actual outcome test",
        candidate_agreement=alternative_candidate,
        changed_variables={},
        unchanged_variables={},
        scenario_assumptions={},
    )
    pred_res = sim.simulate_scenario(sample_baseline, sc)

    actual = ActualOutcomeInput(
        simulation_result_id="TEST-SIM-RES-ID",
        actual_supplier_id="SUP-ALT-02",
        actual_cost=pred_res.predicted_cost * 1.02,
        actual_delivery_days=int(np.ceil(pred_res.predicted_delivery_days)),
        actual_inventory=pred_res.predicted_inventory - 50,
        actual_stockout_rate=pred_res.stockout_probability,
        actual_service_level=pred_res.predicted_service_level,
        actual_customer_impact=pred_res.customer_impact.customer_impact_score,
    )

    eval_result = CNTValidator.evaluate_prediction_vs_actual(pred_res, actual)
    assert eval_result.mae >= 0.0
    assert eval_result.rmse >= 0.0
    assert eval_result.mape < 10.0
    assert eval_result.is_within_tolerance is True


# ==============================================================================
# 10. FULL ENGINE, PERSISTENCE & DATABASE INTEGRATION
# ==============================================================================

def test_18_full_cnt_engine_simulation_and_database_persistence():
    """Runs complete CNTEngine pipeline using actual PostgreSQL tables and verifies DB records."""
    db = SessionLocal()
    try:
        prod = db.query(ProductDB).first()
        if not prod:
            pytest.skip("No product in database")

        engine = CNTEngine(db=db)
        req = CNTSimulationRequest(
            product_id=str(prod.id),
            order_quantity=500,
            config=SimulationConfig(num_monte_carlo_runs=25, random_seed=42),
            scenarios_to_generate=[ScenarioType.NORMAL, ScenarioType.HIGH_DEMAND, ScenarioType.SUPPLIER_DELAY],
        )

        resp = engine.simulate(req)
        assert resp.simulation_id.startswith("RUN-")
        assert resp.baseline.product_id == str(prod.id)
        assert len(resp.scenarios) >= 3
        assert len(resp.recommendation_candidates) >= 1
        assert "1. WHAT CHANGED:" in resp.explanation

        # Verify DB persistence
        sim_run = db.query(SimulationRunDB).filter(SimulationRunDB.run_id == resp.simulation_id).first()
        assert sim_run is not None
        assert sim_run.status == "COMPLETED"
        assert len(sim_run.scenarios) >= 3
    finally:
        db.close()


def test_19_no_data_leakage_timestamp_cutoff():
    """Ensures state builder excludes records created strictly after decision timestamp cutoff."""
    db = SessionLocal()
    try:
        prod = db.query(ProductDB).first()
        if not prod:
            pytest.skip("No product in database")

        past_cutoff = datetime.utcnow() - timedelta(days=365)
        builder = StateBuilder(db=db)
        state_past = builder.build_state(product_id=str(prod.id), decision_timestamp=past_cutoff)

        now_cutoff = datetime.utcnow()
        state_now = builder.build_state(product_id=str(prod.id), decision_timestamp=now_cutoff)

        assert state_past.data_cutoff_timestamp == past_cutoff
        assert state_now.data_cutoff_timestamp == now_cutoff
    finally:
        db.close()


# ==============================================================================
# 11. ABLATION STUDY TESTING
# ==============================================================================

def test_20_ablation_study_runner(sample_baseline, alternative_candidate):
    """Executes the research ablation study across the 5 algorithmic regimes."""
    runner = AblationStudyRunner(engine=CNTEngine())
    study = runner.run_ablation_study(sample_baseline, [alternative_candidate])

    assert "ablation_results" in study
    assert "Rule-Based Selection" in study["ablation_results"]
    assert "ML-Only Prediction" in study["ablation_results"]
    assert "Simulation-Only CNT" in study["ablation_results"]
    assert "ML + Simulation CNT" in study["ablation_results"]
    assert "Full RIMBERIO (Multi-Agent + CNT)" in study["ablation_results"]
    assert study["winning_method"] == "Full RIMBERIO (Multi-Agent + CNT)"
    assert len(study["findings"]) == 4


# ==============================================================================
# 12. ERROR HANDLING & VALIDATION CHECKS
# ==============================================================================

def test_21_invalid_simulation_config_monte_carlo_bounds():
    """Fails validation if num_monte_carlo_runs is outside legal range."""
    with pytest.raises(ValidationError):
        SimulationConfig(num_monte_carlo_runs=5)  # minimum is 10


def test_22_invalid_candidate_negative_price():
    """Fails validation if proposed unit price is non-positive."""
    with pytest.raises(ValidationError):
        CandidateAgreement(
            supplier_id="SUP-ERR",
            proposed_unit_price=-10.0,
            proposed_quantity=100,
            proposed_lead_time_days=5,
        )


def test_23_invalid_candidate_zero_quantity():
    """Fails validation if order quantity is zero."""
    with pytest.raises(ValidationError):
        CandidateAgreement(
            supplier_id="SUP-ERR",
            proposed_unit_price=50.0,
            proposed_quantity=0,
            proposed_lead_time_days=5,
        )


# ==============================================================================
# 13. API ENDPOINTS & COMPOUND SHOCK INTEGRATION
# ==============================================================================

def test_24_compound_disruption_scenario_simulation(sample_baseline, alternative_candidate):
    """Simulates multi-vector compound shock (high demand + delay + freight surge + inventory drain)."""
    cfg = SimulationConfig(num_monte_carlo_runs=50, random_seed=42)
    sim = CNTSimulator(config=cfg)
    sc = CounterfactualScenario(
        scenario_id="SCEN-COMPOUND-TEST",
        scenario_type=ScenarioType.COMPOUND_DISRUPTION,
        description="Compound disruption stress test",
        candidate_agreement=alternative_candidate,
        changed_variables={"supplier_id": alternative_candidate.supplier_id},
        unchanged_variables={},
        scenario_assumptions={
            "demand_shock_multiplier": 1.30,
            "lead_time_drift_days": 6.0,
            "freight_surge_multiplier": 1.50,
            "inventory_depletion_shock_units": int(sample_baseline.current_inventory * 0.4),
        },
    )
    res = sim.simulate_scenario(sample_baseline, sc)
    assert res.predicted_cost > alternative_candidate.proposed_unit_price * alternative_candidate.proposed_quantity
    assert res.predicted_delivery_days > alternative_candidate.proposed_lead_time_days
    assert res.predicted_risk >= 30.0


def test_25_fastapi_cnt_simulate_endpoint():
    """Validates /api/v1/cnt/simulate route function and downstream getters."""
    from backend.app.api.cnt import (
        run_counterfactual_simulation,
        get_simulation_run,
        get_simulation_comparison,
        get_simulation_sensitivity,
        get_simulation_customer_impact,
    )

    db = SessionLocal()
    try:
        prod = db.query(ProductDB).first()
        if not prod:
            pytest.skip("No product in DB")

        req = CNTSimulationRequest(
            product_id=str(prod.id),
            order_quantity=400,
            config=SimulationConfig(num_monte_carlo_runs=20, random_seed=42),
            scenarios_to_generate=[ScenarioType.NORMAL, ScenarioType.HIGH_DEMAND],
        )
        resp = run_counterfactual_simulation(request=req, db=db)
        assert resp.simulation_id.startswith("RUN-")
        assert len(resp.scenarios) >= 2
        assert len(resp.recommendation_candidates) >= 1

        # Test subsequent get_simulation_run
        sim_id = resp.simulation_id
        get_resp = get_simulation_run(simulation_id=sim_id, db=db)
        assert get_resp.simulation_id == sim_id

        # Test get_simulation_comparison
        comp_resp = get_simulation_comparison(simulation_id=sim_id, db=db)
        assert len(comp_resp.pareto_frontier) >= 1

        # Test get_simulation_sensitivity
        sens_resp = get_simulation_sensitivity(simulation_id=sim_id, db=db)
        assert len(sens_resp) >= 1

        # Test get_simulation_customer_impact
        ci_resp = get_simulation_customer_impact(simulation_id=sim_id, db=db)
        assert len(ci_resp) >= 2
    finally:
        db.close()


def test_26_fastapi_cnt_scenarios_generation_endpoint():
    """Validates /api/v1/cnt/scenarios route function without full simulation."""
    from backend.app.api.cnt import generate_scenarios

    db = SessionLocal()
    try:
        prod = db.query(ProductDB).first()
        if not prod:
            pytest.skip("No product in DB")

        scenarios = generate_scenarios(
            product_id=str(prod.id),
            db=db,
        )
        assert len(scenarios) >= 5
        types = [s.scenario_type for s in scenarios]
        assert ScenarioType.NORMAL in types
    finally:
        db.close()


def test_27_fastapi_ablation_study_endpoint():
    """Validates /api/v1/cnt/ablation-study route function."""
    from backend.app.api.cnt import run_ablation_study

    db = SessionLocal()
    try:
        prod = db.query(ProductDB).first()
        if not prod:
            pytest.skip("No product in DB")

        data = run_ablation_study(
            product_id=str(prod.id),
            db=db,
        )
        assert "ablation_results" in data
        assert "winning_method" in data
        assert data["winning_method"] == "Full RIMBERIO (Multi-Agent + CNT)"
    finally:
        db.close()


def test_28_fastapi_actual_outcome_recording_endpoint():
    """Validates /api/v1/cnt/actual-outcome route function."""
    from backend.app.api.cnt import record_actual_decision_outcome

    db = SessionLocal()
    try:
        prod = db.query(ProductDB).first()
        sup = db.query(SupplierDB).first()
        if not prod or not sup:
            pytest.skip("No product or supplier in DB")

        payload = ActualOutcomeInput(
            simulation_result_id=str(prod.id),
            actual_supplier_id=str(sup.id),
            actual_cost=45000.0,
            actual_delivery_days=12,
            actual_inventory=1800,
            actual_stockout_rate=0.02,
            actual_service_level=97.5,
            actual_customer_impact=10.0,
        )
        data = record_actual_decision_outcome(outcome=payload, db=db)
        assert data.mae >= 0.0
        assert data.rmse >= 0.0
        assert data.is_within_tolerance is True
    finally:
        db.close()


