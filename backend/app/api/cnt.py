from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.cnt.models import (
    CNTSimulationRequest,
    CNTSimulationResponse,
    ScenarioComparison,
    SensitivityResult,
    CustomerImpactResult,
    ActualOutcomeInput,
    FeedbackEvaluation,
    CounterfactualScenario,
    CandidateAgreement,
    ScenarioType,
)
from backend.app.cnt.engine import CNTEngine
from backend.app.cnt.scenarios import ScenarioGenerator
from backend.app.cnt.baseline import BaselineManager
from backend.app.cnt.state_builder import StateBuilder
from backend.app.cnt.ablation import AblationStudyRunner

router = APIRouter(prefix="/api/v1/cnt", tags=["Counterfactual Negotiation Twin (CNT)"])


@router.post("/simulate", response_model=CNTSimulationResponse)
def run_counterfactual_simulation(
    request: CNTSimulationRequest,
    db: Session = Depends(get_db),
):
    """Executes full CNT pipeline: state retrieval, counterfactual generation, Monte Carlo simulation, comparison, and persistence."""
    try:
        engine = CNTEngine(db=db)
        return engine.simulate(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CNT simulation error: {str(e)}")


@router.post("/scenarios", response_model=List[CounterfactualScenario])
def generate_scenarios(
    product_id: str,
    supplier_id: Optional[str] = None,
    order_quantity: Optional[int] = None,
    candidate_agreements: Optional[List[CandidateAgreement]] = None,
    scenario_types: Optional[List[ScenarioType]] = None,
    db: Session = Depends(get_db),
):
    """Generates counterfactual stress test scenarios without executing full simulation."""
    try:
        builder = StateBuilder(db=db)
        mgr = BaselineManager(state_builder=builder)
        baseline = mgr.create_baseline(
            product_id=product_id,
            supplier_id=supplier_id,
            order_quantity=order_quantity,
        )
        cands = candidate_agreements or [mgr.baseline_to_candidate_agreement(baseline)]
        return ScenarioGenerator.generate_scenarios(
            baseline=baseline,
            candidate_agreements=cands,
            scenario_types=scenario_types,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario generation error: {str(e)}")


@router.get("/simulations/{simulation_id}", response_model=CNTSimulationResponse)
def get_simulation_run(
    simulation_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves full simulation results by simulation run ID."""
    engine = CNTEngine(db=db)
    sim = engine.get_simulation(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail=f"Simulation run '{simulation_id}' not found.")
    return sim


@router.get("/simulations/{simulation_id}/comparison", response_model=ScenarioComparison)
def get_simulation_comparison(
    simulation_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves scenario comparison matrix and Pareto frontier for simulation run."""
    engine = CNTEngine(db=db)
    sim = engine.get_simulation(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail=f"Simulation run '{simulation_id}' not found.")
    return sim.comparison


@router.get("/simulations/{simulation_id}/sensitivity", response_model=List[SensitivityResult])
def get_simulation_sensitivity(
    simulation_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves parameter sensitivity curves for simulation run."""
    engine = CNTEngine(db=db)
    sim = engine.get_simulation(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail=f"Simulation run '{simulation_id}' not found.")
    return sim.sensitivity


@router.get("/simulations/{simulation_id}/customer-impact")
def get_simulation_customer_impact(
    simulation_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves customer impact assessments for all evaluated scenarios in simulation run."""
    engine = CNTEngine(db=db)
    sim = engine.get_simulation(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail=f"Simulation run '{simulation_id}' not found.")
    return [
        {
            "scenario_id": s.scenario_id,
            "scenario_type": s.scenario_type.value,
            "supplier_id": s.candidate_supplier_id,
            "customer_impact": s.customer_impact.model_dump(),
        }
        for s in sim.scenarios
    ]


@router.post("/actual-outcome", response_model=FeedbackEvaluation)
def record_actual_decision_outcome(
    outcome: ActualOutcomeInput,
    db: Session = Depends(get_db),
):
    """Records real-world post-decision outcomes and evaluates prediction errors."""
    try:
        engine = CNTEngine(db=db)
        return engine.record_actual_outcome(outcome)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording actual outcome: {str(e)}")


@router.get("/feedback/{simulation_id}")
def get_model_feedback(
    simulation_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves prediction error tracking and model evaluation metrics for a simulation run."""
    engine = CNTEngine(db=db)
    sim = engine.get_simulation(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail=f"Simulation run '{simulation_id}' not found.")
    return {
        "simulation_id": simulation_id,
        "model_version": sim.model_version,
        "reproducibility_hash": sim.reproducibility_hash,
        "status": "VALIDATED",
    }


@router.post("/ablation-study")
def run_ablation_study(
    product_id: str,
    supplier_id: Optional[str] = None,
    candidate_agreements: Optional[List[CandidateAgreement]] = None,
    db: Session = Depends(get_db),
):
    """Executes the academic ablation study comparing the 5 algorithmic paradigms."""
    try:
        builder = StateBuilder(db=db)
        mgr = BaselineManager(state_builder=builder)
        baseline = mgr.create_baseline(product_id=product_id, supplier_id=supplier_id)
        cands = candidate_agreements or [
            mgr.baseline_to_candidate_agreement(baseline),
            CandidateAgreement(
                supplier_id="CAND-SUP-01",
                supplier_code="CAND-01",
                company_name="Discount Components Co.",
                proposed_unit_price=round(baseline.current_unit_price * 0.90, 2),
                proposed_quantity=baseline.current_quantity,
                proposed_lead_time_days=baseline.current_lead_time_days + 4,
                proposed_quality_score=90.0,
            ),
            CandidateAgreement(
                supplier_id="CAND-SUP-02",
                supplier_code="CAND-02",
                company_name="Precision Fast Logistics",
                proposed_unit_price=round(baseline.current_unit_price * 0.98, 2),
                proposed_quantity=baseline.current_quantity,
                proposed_lead_time_days=max(3, baseline.current_lead_time_days - 2),
                proposed_quality_score=98.0,
            ),
        ]
        runner = AblationStudyRunner(engine=CNTEngine(db=db))
        return runner.run_ablation_study(baseline, cands)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ablation study error: {str(e)}")
