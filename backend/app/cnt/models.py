from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field, field_validator


class ScenarioType(str, Enum):
    NORMAL = "NORMAL"
    HIGH_DEMAND = "HIGH_DEMAND"
    LOW_DEMAND = "LOW_DEMAND"
    SUPPLIER_DELAY = "SUPPLIER_DELAY"
    TRANSPORT_DISRUPTION = "TRANSPORT_DISRUPTION"
    SUPPLY_SHORTAGE = "SUPPLY_SHORTAGE"
    PRICE_INCREASE = "PRICE_INCREASE"
    INVENTORY_SHORTAGE = "INVENTORY_SHORTAGE"
    QUALITY_DEGRADATION = "QUALITY_DEGRADATION"
    CAPACITY_REDUCTION = "CAPACITY_REDUCTION"
    COMPOUND_DISRUPTION = "COMPOUND_DISRUPTION"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ImpactLevel(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CostAssumptions(BaseModel):
    holding_cost_annual_rate: float = Field(default=0.20, ge=0.0, description="Annual inventory holding cost rate (e.g. 20%)")
    stockout_cost_per_unit: float = Field(default=25.0, ge=0.0, description="Penalty cost per unit of unsatisfied demand")
    delay_cost_per_day: float = Field(default=150.0, ge=0.0, description="Daily operational penalty for delayed fulfillment")
    quality_failure_multiplier: float = Field(default=2.5, ge=1.0, description="Multiplier on unit cost for defect handling/returns")
    switching_fixed_cost: float = Field(default=1500.0, ge=0.0, description="One-time qualification/administrative switching cost")
    expediting_fee_per_unit: float = Field(default=12.0, ge=0.0, description="Expedited freight fee per emergency unit")
    time_horizon_days: int = Field(default=30, gt=0, description="Simulation planning horizon in days")


class MultiObjectiveWeights(BaseModel):
    cost_weight: float = Field(default=0.35, ge=0.0, le=1.0)
    delivery_weight: float = Field(default=0.20, ge=0.0, le=1.0)
    quality_weight: float = Field(default=0.15, ge=0.0, le=1.0)
    reliability_weight: float = Field(default=0.10, ge=0.0, le=1.0)
    risk_weight: float = Field(default=0.10, ge=0.0, le=1.0)
    service_weight: float = Field(default=0.10, ge=0.0, le=1.0)

    @field_validator("service_weight")
    @classmethod
    def validate_sum(cls, v: float, values: Any) -> float:
        # Normalize or check tolerance
        return v


class SimulationConfig(BaseModel):
    num_monte_carlo_runs: int = Field(default=500, ge=10, le=10000)
    random_seed: int = Field(default=42)
    model_version: str = Field(default="CNT_V2.0_EXP")
    training_data_version: str = Field(default="DATA_SNAPSHOT_2026_Q4")
    cost_assumptions: CostAssumptions = Field(default_factory=CostAssumptions)
    weights: MultiObjectiveWeights = Field(default_factory=MultiObjectiveWeights)
    decision_timestamp: Optional[datetime] = Field(default=None, description="Cutoff timestamp to strictly avoid data leakage")


class CandidateAgreement(BaseModel):
    supplier_id: str
    supplier_code: Optional[str] = None
    company_name: Optional[str] = None
    proposed_unit_price: float = Field(gt=0.0)
    proposed_quantity: int = Field(gt=0)
    proposed_lead_time_days: int = Field(gt=0)
    proposed_quality_score: float = Field(default=95.0, ge=0.0, le=100.0)
    proposed_capacity: Optional[int] = Field(default=50000, gt=0)
    payment_terms: str = Field(default="Net 30")
    transport_cost: float = Field(default=1000.0, ge=0.0)
    is_incumbent: bool = Field(default=False)


class BaselineState(BaseModel):
    snapshot_id: str
    snapshot_hash: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    product_id: str
    product_sku: str
    product_name: str
    supplier_id: str
    supplier_code: str
    supplier_name: str
    current_unit_price: float
    current_lead_time_days: int
    current_quantity: int
    current_inventory: int = Field(ge=0)
    safety_stock: int = Field(ge=0)
    reorder_point: int = Field(ge=0)
    daily_demand_mean: float = Field(gt=0.0)
    daily_demand_std: float = Field(ge=0.0)
    forecast_demand_30d: float = Field(gt=0.0)
    supplier_historical_reliability: float = Field(ge=0.0, le=1.0)
    supplier_historical_defect_rate: float = Field(ge=0.0, le=1.0)
    supplier_lead_time_std: float = Field(ge=0.0)
    supplier_capacity: int = Field(gt=0)
    pending_customer_orders_count: int = Field(ge=0)
    total_customer_order_units: int = Field(ge=0)
    active_shipments_count: int = Field(ge=0)
    current_service_level: float = Field(ge=0.0, le=100.0)
    current_risk_score: float = Field(ge=0.0, le=100.0)
    data_cutoff_timestamp: Optional[datetime] = None


class CounterfactualScenario(BaseModel):
    scenario_id: str
    scenario_type: ScenarioType
    description: str
    candidate_agreement: CandidateAgreement
    changed_variables: Dict[str, Any]
    unchanged_variables: Dict[str, Any]
    scenario_assumptions: Dict[str, Any]


class CostBreakdown(BaseModel):
    purchase_cost: float
    transportation_cost: float
    holding_cost: float
    stockout_cost: float
    quality_failure_cost: float
    delay_cost: float
    switching_cost: float
    expediting_cost: float
    total_landed_cost: float


class UncertaintyRange(BaseModel):
    mean: float
    median: float
    p10: float
    p50: float
    p90: float
    std_dev: float
    min_val: float
    max_val: float
    confidence: float = Field(ge=0.0, le=1.0)


class CustomerImpactResult(BaseModel):
    affected_customers: List[str] = Field(default_factory=list)
    affected_orders: List[str] = Field(default_factory=list)
    expected_delay_days: float = 0.0
    service_level_change: float = 0.0  # e.g. -2.5%
    revenue_at_risk: float = 0.0
    customer_impact_score: float = 0.0  # 0 to 100
    impact_level: ImpactLevel = ImpactLevel.LOW
    reasoning: str = ""


class ScenarioSimulationResult(BaseModel):
    scenario_id: str
    scenario_type: ScenarioType
    candidate_supplier_id: str
    candidate_supplier_name: str
    predicted_cost: float
    cost_range: UncertaintyRange
    cost_breakdown: CostBreakdown
    predicted_delivery_days: float
    delivery_range: UncertaintyRange
    predicted_delivery_delay: float
    stockout_probability: float  # e.g. 0.05 for 5%
    stockout_quantity_expected: float
    predicted_inventory: int
    predicted_risk: float  # 0 to 100
    risk_level: RiskLevel
    risk_factors: List[str] = Field(default_factory=list)
    predicted_service_level: float  # 0 to 100
    customer_impact: CustomerImpactResult
    confidence: float = Field(ge=0.0, le=1.0)
    changed_variables: Dict[str, Any]
    unchanged_variables: Dict[str, Any]
    scenario_assumptions: Dict[str, Any]


class ComparisonMetricDelta(BaseModel):
    cost_delta: float
    cost_pct_delta: float
    delivery_delta: float
    delivery_pct_delta: float
    risk_delta: float
    inventory_delta: int
    service_level_delta: float
    customer_impact_delta: float


class RankedCandidate(BaseModel):
    rank: int
    scenario_id: str
    supplier_id: str
    supplier_name: str
    overall_score: float  # 0 to 100
    price_score: float
    delivery_score: float
    quality_score: float
    reliability_score: float
    risk_score: float
    service_score: float
    is_pareto_optimal: bool
    recommendation_rationale: str


class ScenarioComparison(BaseModel):
    baseline_scenario_id: str
    scenarios: List[ScenarioSimulationResult]
    deltas: Dict[str, ComparisonMetricDelta]  # keyed by scenario_id
    pareto_frontier: List[str]  # scenario_ids
    rankings: List[RankedCandidate]


class SensitivityPoint(BaseModel):
    parameter_name: str
    variation_pct: float  # e.g. -10, 0, +10, +20
    parameter_value: float
    predicted_cost: float
    predicted_delivery_days: float
    stockout_probability: float
    cost_elasticity: float


class SensitivityResult(BaseModel):
    parameter_name: str
    baseline_value: float
    sensitivity_curve: List[SensitivityPoint]
    sensitivity_score: float  # Impact rating 0-100
    explanation: str


class ActualOutcomeInput(BaseModel):
    simulation_result_id: str
    actual_supplier_id: str
    actual_cost: float = Field(ge=0.0)
    actual_delivery_days: int = Field(ge=1)
    actual_inventory: int = Field(ge=0)
    actual_stockout_rate: float = Field(ge=0.0, le=1.0)
    actual_service_level: float = Field(ge=0.0, le=100.0)
    actual_customer_impact: float = Field(ge=0.0)
    recorded_at: Optional[datetime] = None


class MetricError(BaseModel):
    metric_name: str
    predicted_value: float
    actual_value: float
    error: float
    absolute_error: float
    percentage_error: float


class FeedbackEvaluation(BaseModel):
    prediction_actual_id: str
    simulation_result_id: str
    metrics: List[MetricError]
    mae: float
    rmse: float
    mape: float
    model_version: str
    is_within_tolerance: bool


class CNTSimulationRequest(BaseModel):
    product_id: str
    supplier_id: Optional[str] = None
    order_quantity: Optional[int] = Field(default=None, gt=0)
    candidate_agreements: Optional[List[CandidateAgreement]] = None
    scenarios_to_generate: Optional[List[ScenarioType]] = None
    config: Optional[SimulationConfig] = None


class CNTSimulationResponse(BaseModel):
    simulation_id: str
    baseline: BaselineState
    scenarios: List[ScenarioSimulationResult]
    comparison: ScenarioComparison
    sensitivity: List[SensitivityResult]
    recommendation_candidates: List[RankedCandidate]
    explanation: str
    execution_time_ms: float
    model_version: str
    reproducibility_hash: str
