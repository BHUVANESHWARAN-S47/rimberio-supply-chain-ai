from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

# ==============================================================================
# 1. Customization Schemas
# ==============================================================================

class CriteriaWeightsConfig(BaseModel):
    cost: float = Field(0.30, ge=0.0, le=1.0, description="Weight for purchase/landed cost")
    quality: float = Field(0.25, ge=0.0, le=1.0, description="Weight for supplier quality score")
    delivery: float = Field(0.20, ge=0.0, le=1.0, description="Weight for on-time delivery rate")
    reliability: float = Field(0.15, ge=0.0, le=1.0, description="Weight for vendor reliability track record")
    risk: float = Field(0.10, ge=0.0, le=1.0, description="Weight for geopolitical and route risk index")

class AgentHeuristicsConfig(BaseModel):
    buyer_target_price: float = Field(142.50, description="Target procurement unit price ($)")
    buyer_reservation_price: float = Field(155.00, description="Maximum ceiling price ($)")
    supplier_asking_price: float = Field(165.00, description="Initial vendor quote ($)")
    supplier_reservation_price: float = Field(145.00, description="Vendor floor price ($)")
    max_rounds: int = Field(10, ge=1, le=50, description="Max autonomous negotiation rounds")
    concession_strategy: str = Field("boulware", description="boulware | linear | conceder | adaptive")
    concession_beta: float = Field(2.5, description="Boulware beta parameter (>1 firm, <1 eager)")
    llm_provider: str = Field("heuristic_rule_engine", description="heuristic_rule_engine | openai | anthropic | local_ollama")
    system_prompt_override: Optional[str] = Field(None, description="Custom LLM persona prompt")

class SimulationConfig(BaseModel):
    monte_carlo_runs: int = Field(500, ge=50, le=10000, description="Number of Monte Carlo trials")
    default_demand_surge_percent: float = Field(25.0, description="Default demand surge percentage (+%)")
    default_lead_time_drift_days: int = Field(6, description="Default maritime/freight delay in days")
    cost_sensitivity_factor: float = Field(1.2, description="Freight cost escalation multiplier")
    confidence_interval: float = Field(0.95, description="Statistical confidence interval (0.90, 0.95, 0.99)")

class DecisionPolicyConfig(BaseModel):
    switch_score_delta_threshold: float = Field(0.10, description="Minimum score improvement to trigger Switch")
    critical_risk_threshold: float = Field(0.65, description="Risk score threshold triggering mandatory switch/negotiate")
    max_allowable_switching_cost: float = Field(50000.0, description="Maximum budget allowed for supplier onboarding")
    auto_apply_recommendations: bool = Field(False, description="Whether to automatically apply AI decisions")

class NotificationTemplatesConfig(BaseModel):
    email_subject: str = Field(
        "CRITICAL SUPPLY CHAIN ADVISORY: Revised Delivery Schedule for Order #{order_id}",
        description="Customer notification email subject line"
    )
    email_body: str = Field(
        "Dear {customer_name},\n\nWe are writing to inform you of an operational routing adjustment affecting order #{order_id} ({sku_name}). Due to {disruption_reason}, the revised expected delivery date is {revised_delivery_date} (delay of approximately {delay_days} business days).\n\nOur autonomous mitigation engine has secured priority freight to minimize further exposure.\n\nSincerely,\nRimberio Supply Chain Operations",
        description="Customer advisory notification template"
    )
    sms_body: str = Field(
        "Rimberio Notice: Order #{order_id} has a revised ETA of {revised_delivery_date} due to {disruption_reason}.",
        description="SMS alert message template"
    )

class FullCustomizationProfile(BaseModel):
    profile_id: str = "default_enterprise"
    organization_name: str = "Rimberio Global Dynamics"
    weights: CriteriaWeightsConfig = Field(default_factory=CriteriaWeightsConfig)
    agent_heuristics: AgentHeuristicsConfig = Field(default_factory=AgentHeuristicsConfig)
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
    policy: DecisionPolicyConfig = Field(default_factory=DecisionPolicyConfig)
    notifications: NotificationTemplatesConfig = Field(default_factory=NotificationTemplatesConfig)

# ==============================================================================
# 2. Multi-Agent Negotiation Schemas
# ==============================================================================

class NegotiationBid(BaseModel):
    round: int
    agent_id: str
    agent_name: str
    role: str
    proposed_price: float
    proposed_lead_time_days: int
    proposed_sla_confidence: float
    message: str
    status: str

class NegotiationSession(BaseModel):
    session_id: str
    supplier_code: str
    supplier_name: str
    sku_code: str
    current_round: int
    max_rounds: int
    status: str  # ACTIVE | CONVERGED | DEADLOCKED
    buyer_target: float
    supplier_target: float
    current_offer: float
    agreed_lead_time: str
    agent_confidence: float
    estimated_savings: float
    history: List[NegotiationBid] = []

class NegotiationStepRequest(BaseModel):
    session_id: str
    force_concession: Optional[bool] = False
    custom_buyer_offer: Optional[float] = None

# ==============================================================================
# 3. Counterfactual Simulation Schemas
# ==============================================================================

class CounterfactualSimulationRequest(BaseModel):
    supplier_code: str = "SUP-001"
    disruption_scenario: str = "Suez Canal Congestion & Delay"
    demand_surge_percent: float = 25.0
    lead_time_drift_days: int = 6
    freight_cost_surge_percent: float = 15.0
    monte_carlo_samples: Optional[int] = 500

class SimulationOutcome(BaseModel):
    supplier_code: str
    supplier_name: str
    scenario_tested: str
    expected_cost_impact: float
    cost_impact_p95: float
    stockout_probability: float
    sla_breach_probability: float
    expected_delay_days: float
    counterfactual_net_saving: float
    risk_level: str
    distribution_samples: List[float] = []

# ==============================================================================
# 4. Supplier & Decision Schemas
# ==============================================================================

class SupplierProfile(BaseModel):
    code: str
    name: str
    tier: str
    country: str
    unit_cost: float
    quality_score: float  # 0 to 100
    on_time_delivery_rate: float  # 0 to 100
    reliability_index: float  # 0 to 100
    risk_score: float  # 0 to 100
    composite_score: Optional[float] = None
    capacity_monthly: int
    status: str

class DecisionEvaluationRequest(BaseModel):
    sku_code: str = "SKU-MC-772"
    current_supplier_code: str = "SUP-001"
    candidate_supplier_codes: List[str] = ["SUP-002", "SUP-003", "SUP-004", "SUP-005"]

class DecisionOutcome(BaseModel):
    sku_code: str
    recommendation: str  # RETAIN | NEGOTIATE | SWITCH
    confidence: float
    current_supplier: SupplierProfile
    recommended_supplier: Optional[SupplierProfile] = None
    net_cost_impact: float
    composite_score_delta: float
    decision_rationale: List[str]

# ==============================================================================
# 5. Customer Impact & Notification Schemas
# ==============================================================================

class ImpactedCustomerOrder(BaseModel):
    order_id: str
    customer_name: str
    customer_tier: str
    contact_email: str
    sku_code: str
    quantity: int
    promised_eta: str
    revised_eta: str
    delay_days: int
    sla_penalty_exposure: float
    status: str

class BatchNotificationRequest(BaseModel):
    order_ids: List[str]
    disruption_reason: Optional[str] = "Global maritime route transit delay"
    channel: str = "EMAIL"

class NotificationDispatchResult(BaseModel):
    total_dispatched: int
    dispatched_orders: List[str]
    sample_rendered_subject: str
    sample_rendered_message: str
    status: str

# ==============================================================================
# 6. Continuous Learning & Feedback Schemas
# ==============================================================================

class LearningMetricsResponse(BaseModel):
    accuracy: str
    mae_lead_time_days: float
    rmse_lead_time_days: float
    mape_cost_percent: float
    total_evaluated_cycles: int
    active_policy_version: str
    last_calibrated_at: str
    confusion_matrix: Dict[str, Dict[str, int]]
