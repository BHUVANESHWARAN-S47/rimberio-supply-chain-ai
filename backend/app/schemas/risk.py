from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from backend.app.schemas.common import RiskLevel


class RiskCategory(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    GEOPOLITICAL = "GEOPOLITICAL"
    FINANCIAL = "FINANCIAL"
    DEPENDENCY = "DEPENDENCY"
    CLIMATE = "CLIMATE"
    COMPLIANCE = "COMPLIANCE"


class RiskInput(BaseModel):
    """Input parameters for Risk Assessment Agent."""
    supplier_id: str
    supplier_name: Optional[str] = None
    country: str = Field(default="Global", description="Country of supplier headquarters or manufacturing plant")
    single_source: bool = Field(default=False, description="True if no qualified backup supplier currently exists")
    spend_share_pct: float = Field(default=0.20, ge=0.0, le=1.0, description="Fraction of company procurement spend allocated to supplier")
    financial_credit_score: Optional[float] = Field(default=80.0, ge=0.0, le=100.0, description="Financial solvency / credit rating (0-100)")
    disruption_event_history_count: int = Field(default=0, ge=0, description="Logged historical disruption incidents")
    on_time_delivery_rate: float = Field(default=95.0, ge=0.0, le=100.0, description="Historical on-time fulfillment rate percentage")
    quality_defect_rate: float = Field(default=0.015, ge=0.0, le=1.0, description="Historical defective parts fraction")
    climate_exposure_score: Optional[float] = Field(default=20.0, ge=0.0, le=100.0, description="Natural disaster, typhoon, flood risk exposure")
    analyst_notes: Optional[str] = Field(default=None, description="Risk memorandum or compliance audit notes")


class RiskAssessmentResult(BaseModel):
    """Structured empirical risk profile and category scores."""
    supplier_id: str
    composite_risk_score: float = Field(ge=0.0, le=100.0)
    risk_level: RiskLevel
    category_scores: Dict[str, float]
    key_risk_drivers: List[str]
    mitigation_recommendations: List[str]
    is_single_source_hazard: bool
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    adversarial_flags: List[str] = Field(default_factory=list)
