import json
import os
from threading import Lock
from typing import Optional
from backend.models.schemas import (
    FullCustomizationProfile,
    CriteriaWeightsConfig,
    AgentHeuristicsConfig,
    SimulationConfig,
    DecisionPolicyConfig,
    NotificationTemplatesConfig,
)

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "customization_profile.json")

class CustomizationStore:
    def __init__(self):
        self._lock = Lock()
        self._profile: FullCustomizationProfile = FullCustomizationProfile()
        self._load_from_disk()

    def _load_from_disk(self):
        try:
            if os.path.exists(CONFIG_FILE_PATH):
                with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._profile = FullCustomizationProfile(**data)
            else:
                self._persist_to_disk()
        except Exception as e:
            print(f"[CustomizationStore] Warning: could not load customization from disk: {e}")
            self._profile = FullCustomizationProfile()

    def _persist_to_disk(self):
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
            with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self._profile.model_dump(), f, indent=2)
        except Exception as e:
            print(f"[CustomizationStore] Warning: could not persist customization: {e}")

    def get_profile(self) -> FullCustomizationProfile:
        with self._lock:
            return self._profile.model_copy(deep=True)

    def update_profile(self, new_profile: FullCustomizationProfile) -> FullCustomizationProfile:
        with self._lock:
            self._profile = new_profile
            self._persist_to_disk()
            return self._profile.model_copy(deep=True)

    def update_weights(self, weights: CriteriaWeightsConfig) -> CriteriaWeightsConfig:
        with self._lock:
            self._profile.weights = weights
            self._persist_to_disk()
            return self._profile.weights.model_copy()

    def update_agent_heuristics(self, heuristics: AgentHeuristicsConfig) -> AgentHeuristicsConfig:
        with self._lock:
            self._profile.agent_heuristics = heuristics
            self._persist_to_disk()
            return self._profile.agent_heuristics.model_copy()

    def update_simulation_config(self, sim: SimulationConfig) -> SimulationConfig:
        with self._lock:
            self._profile.simulation = sim
            self._persist_to_disk()
            return self._profile.simulation.model_copy()

    def reset_to_defaults(self) -> FullCustomizationProfile:
        with self._lock:
            self._profile = FullCustomizationProfile()
            self._persist_to_disk()
            return self._profile.model_copy(deep=True)

customization_store = CustomizationStore()
