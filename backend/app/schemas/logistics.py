from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class ShippingMode(str, Enum):
    AIR = "AIR"
    OCEAN = "OCEAN"
    ROAD = "ROAD"
    RAIL = "RAIL"
    MULTIMODAL = "MULTIMODAL"


class PortStatus(str, Enum):
    NORMAL = "NORMAL"
    CONGESTED = "CONGESTED"
    CRITICAL_BOTTLENECK = "CRITICAL_BOTTLENECK"


class LogisticsInput(BaseModel):
    """Input payload for Logistics Agent evaluation."""
    origin_country: str = Field(min_length=2, description="Country of departure or manufacturer origin")
    destination_country: str = Field(min_length=2, description="Destination port or warehouse country")
    distance_km: float = Field(gt=0.0, description="Transit route distance in kilometers")
    shipment_weight_kg: float = Field(gt=0.0, description="Total physical gross weight in kilograms")
    shipping_mode: ShippingMode = Field(default=ShippingMode.OCEAN, description="Mode of transport")
    carrier_code: Optional[str] = Field(default=None, description="Carrier identifier or maritime shipping line")
    port_status: PortStatus = Field(default=PortStatus.NORMAL, description="Congestion state at transit ports")
    expedited: bool = Field(default=False, description="Whether priority air/express handling is requested")
    customs_clearance_days: float = Field(default=2.0, ge=0.0, description="Expected customs processing duration")
    shipment_notes: Optional[str] = Field(default=None, description="Waybill memo or special handling notes")


class LogisticsResult(BaseModel):
    """Comprehensive deterministic logistics cost, transit, and emissions profile."""
    shipping_mode: ShippingMode
    origin_country: str
    destination_country: str
    distance_km: float
    shipment_weight_kg: float
    estimated_transit_days: float
    min_transit_days: float
    max_transit_days: float
    freight_cost: float
    handling_and_port_fees: float
    total_logistics_cost: float
    cost_per_kg: float
    carbon_emissions_kg_co2: float
    route_risk_score: float = Field(ge=0.0, le=100.0)
    is_carrier_reliable: bool
    reasoning: str
    adversarial_flags: List[str] = Field(default_factory=list)
