from fastapi import APIRouter
from backend.models.schemas import CounterfactualSimulationRequest, SimulationOutcome
from backend.services.counterfactual_twin import counterfactual_twin

router = APIRouter(prefix="/api/simulation", tags=["Counterfactual Negotiation Twin (CNT)"])

@router.post("/counterfactual", response_model=SimulationOutcome)
def run_counterfactual_simulation(req: CounterfactualSimulationRequest):
    """Run Monte Carlo counterfactual simulation with stochastic perturbation modeling."""
    return counterfactual_twin.run_simulation(req)

@router.get("/scenarios")
def list_disruption_scenarios():
    """List standard pre-configured global supply chain disruption scenarios."""
    return [
        {
            "id": "DIS-01",
            "name": "Suez Canal Congestion & Delay",
            "default_delay_days": 6,
            "default_demand_surge": 25.0,
            "freight_surge": 15.0,
            "severity": "CRITICAL"
        },
        {
            "id": "DIS-02",
            "name": "Panama Canal Drought Draft Restrictions",
            "default_delay_days": 9,
            "default_demand_surge": 18.0,
            "freight_surge": 24.0,
            "severity": "HIGH"
        },
        {
            "id": "DIS-03",
            "name": "Semiconductor Wafer Allocation Shortage",
            "default_delay_days": 14,
            "default_demand_surge": 40.0,
            "freight_surge": 8.0,
            "severity": "CRITICAL"
        },
        {
            "id": "DIS-04",
            "name": "Rotterdam Port Automation Terminal Labor Action",
            "default_delay_days": 4,
            "default_demand_surge": 10.0,
            "freight_surge": 12.0,
            "severity": "MODERATE"
        }
    ]
