from fastapi import APIRouter, HTTPException
from backend.models.schemas import (
    FullCustomizationProfile,
    CriteriaWeightsConfig,
    AgentHeuristicsConfig,
    SimulationConfig,
)
from backend.services.customization_store import customization_store

router = APIRouter(prefix="/api/customization", tags=["Customization & Configuration"])

@router.get("/profile", response_model=FullCustomizationProfile)
def get_customization_profile():
    """Retrieve active system customization profile."""
    return customization_store.get_profile()

@router.put("/profile", response_model=FullCustomizationProfile)
def update_customization_profile(profile: FullCustomizationProfile):
    """Update complete customization profile."""
    return customization_store.update_profile(profile)

@router.patch("/weights", response_model=CriteriaWeightsConfig)
def update_criteria_weights(weights: CriteriaWeightsConfig):
    """Update multi-criteria evaluation weights (cost, quality, delivery, reliability, risk)."""
    return customization_store.update_weights(weights)

@router.patch("/agent-heuristics", response_model=AgentHeuristicsConfig)
def update_agent_heuristics(heuristics: AgentHeuristicsConfig):
    """Update multi-agent negotiation heuristics (concession curve beta, target prices, max rounds)."""
    return customization_store.update_agent_heuristics(heuristics)

@router.patch("/simulation", response_model=SimulationConfig)
def update_simulation_config(sim: SimulationConfig):
    """Update Monte Carlo simulation sample sizes and default perturbation shocks."""
    return customization_store.update_simulation_config(sim)

@router.post("/reset-defaults", response_model=FullCustomizationProfile)
def reset_to_defaults():
    """Reset customization back to factory research baselines."""
    return customization_store.reset_to_defaults()
