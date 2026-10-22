from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator

class PriceTrend(str, Enum):
    STABLE = "STABLE"
    INFLATIONARY = "INFLATIONARY"
    DEFLATIONARY = "DEFLATIONARY"

class VolumeDiscountTier(BaseModel):
    """Defines a volume break threshold and the corresponding discount percentage."""
    min_quantity: int = Field(gt=0, description="Minimum order quantity to qualify for this discount tier")
    discount_pct: float = Field(ge=0.0, le=1.0, description="Discount percentage (e.g., 0.05 for 5%)")

class PriceAnalysisInput(BaseModel):
    """Input parameters for the Price Analysis Agent."""
    supplier_id: str
    product_id: str
    quoted_unit_price: float = Field(gt=0.0, description="Unit quotation price from supplier")
    order_quantity: int = Field(gt=0, description="Total order volume in units")
    estimated_transport_cost: float = Field(default=0.0, ge=0.0, description="Total freight and transport cost for batch")
    tariffs_and_duties_pct: float = Field(default=0.0, ge=0.0, le=1.0, description="Customs, import duties, and tariff rate")
    handling_fee_per_unit: float = Field(default=0.0, ge=0.0, description="Per-unit port, packaging, or handling fee")
    current_contract_price: Optional[float] = Field(default=None, ge=0.0, description="Incumbent contract unit price")
    market_benchmark_price: Optional[float] = Field(default=None, ge=0.0, description="Market benchmark unit price")
    historical_prices: Optional[List[float]] = Field(default=None, description="Historical procurement unit prices")
    discount_tiers: Optional[List[VolumeDiscountTier]] = Field(default=None, description="Optional volume discount schedule")
    analysis_notes: Optional[str] = Field(default=None, description="Procurement analyst or RFQ context memo")

class PriceAnalysisResult(BaseModel):
    """Comprehensive deterministic landed cost, benchmark comparison, and savings metrics."""
    supplier_id: str
    product_id: str
    base_unit_price: float
    volume_discount_pct: float
    discounted_unit_price: float
    freight_per_unit: float
    tariffs_per_unit: float
    handling_per_unit: float
    landed_cost_per_unit: float
    total_procurement_cost: float
    benchmark_unit_price: float
    current_contract_unit_price: float
    savings_vs_current: float
    savings_pct_vs_current: float
    price_deviation_vs_benchmark: float
    price_deviation_pct_vs_benchmark: float
    historical_average_price: float
    historical_price_trend: PriceTrend
    is_price_competitive: bool
    reasoning: str
    adversarial_flags: List[str] = Field(default_factory=list)
