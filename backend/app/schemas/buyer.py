from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from backend.app.schemas.common import NegotiationAction

class CriteriaWeights(BaseModel):
    cost: float = Field(0.30, ge=0.0, le=1.0)
    quality: float = Field(0.25, ge=0.0, le=1.0)
    delivery: float = Field(0.20, ge=0.0, le=1.0)
    reliability: float = Field(0.15, ge=0.0, le=1.0)
    risk: float = Field(0.10, ge=0.0, le=1.0)

    @model_validator(mode='after')
    def validate_sum(self):
        total = self.cost + self.quality + self.delivery + self.reliability + self.risk
        if not (0.98 <= total <= 1.02):
            raise ValueError(f"Criteria weights must sum to approximately 1.0, got {total:.3f}")
        return self

class BuyerRequirements(BaseModel):
    quantity: int = Field(..., gt=0, description="Required procurement quantity")
    max_price: float = Field(..., gt=0.0, description="Ceiling price - strictly cannot exceed")
    min_quality: float = Field(90.0, ge=0.0, le=100.0, description="Minimum acceptable quality score")
    max_delivery_days: int = Field(..., gt=0, description="Maximum allowable lead time in days")
    min_reliability: float = Field(80.0, ge=0.0, le=100.0, description="Minimum supplier reliability track record")
    max_risk_score: float = Field(50.0, ge=0.0, le=100.0, description="Maximum allowable risk score")
    acceptable_payment_terms: List[str] = Field(default_factory=lambda: ["Net 30", "Net 60"])
    
    # Negotiation preferences
    target_price: Optional[float] = Field(None, gt=0.0)
    target_delivery_days: Optional[int] = Field(None, gt=0)
    counteroffer_margin_percent: float = Field(15.0, ge=0.0, le=100.0)
    minimum_utility_threshold: float = Field(0.65, ge=0.0, le=1.0)
    weights: CriteriaWeights = Field(default_factory=CriteriaWeights)

    @model_validator(mode='after')
    def validate_targets(self):
        if self.target_price is not None and self.target_price > self.max_price:
            raise ValueError(f"target_price ({self.target_price}) cannot exceed max_price ({self.max_price})")
        if self.target_delivery_days is not None and self.target_delivery_days > self.max_delivery_days:
            raise ValueError(f"target_delivery_days ({self.target_delivery_days}) cannot exceed max_delivery_days ({self.max_delivery_days})")
        return self

class SupplierProposal(BaseModel):
    supplier_id: str = Field(..., min_length=1)
    supplier_name: str = Field(..., min_length=1)
    proposed_unit_price: float = Field(..., ge=0.0)
    proposed_quantity: int = Field(..., ge=0)
    proposed_delivery_days: int = Field(..., ge=0)
    proposed_quality_score: float = Field(..., ge=0.0, le=100.0)
    reliability_index: float = Field(..., ge=0.0, le=100.0)
    risk_score: float = Field(..., ge=0.0, le=100.0)
    payment_terms: str = Field("Net 30")
    notes: Optional[str] = None

class BuyerConstraintViolation(BaseModel):
    constraint_type: str  # PRICE, QUALITY, DELIVERY, RELIABILITY, RISK, PAYMENT_TERMS, QUANTITY
    expected: Any
    actual: Any
    severity: str = "HARD"  # HARD | SOFT
    message: str

class BuyerEvaluationResult(BaseModel):
    supplier_id: str
    recommendation: NegotiationAction
    overall_utility: float = Field(..., ge=0.0, le=1.0)
    hard_constraint_violations: List[BuyerConstraintViolation] = Field(default_factory=list)
    soft_constraint_violations: List[BuyerConstraintViolation] = Field(default_factory=list)
    is_valid: bool = True
    
    # Dimension utilities
    price_utility: float = Field(..., ge=0.0, le=1.0)
    quality_utility: float = Field(..., ge=0.0, le=1.0)
    delivery_utility: float = Field(..., ge=0.0, le=1.0)
    reliability_utility: float = Field(..., ge=0.0, le=1.0)
    risk_utility: float = Field(..., ge=0.0, le=1.0)
    
    # Counteroffer variables if recommendation is COUNTEROFFER
    counteroffer_price: Optional[float] = None
    counteroffer_delivery_days: Optional[int] = None
    counteroffer_quantity: Optional[int] = None
    
    # Audit & Security
    explanation: str
    sanitized_notes: Optional[str] = None
    security_flagged: bool = False
    security_reason: Optional[str] = None
    execution_time_ms: float = 0.0
