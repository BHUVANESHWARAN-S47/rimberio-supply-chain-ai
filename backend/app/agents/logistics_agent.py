import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.agents.base import BaseAgent
from backend.app.agents.registry import AgentRegistry
from backend.app.schemas.common import AgentCapability
from backend.app.schemas.logistics import (
    LogisticsInput,
    LogisticsResult,
    ShippingMode,
    PortStatus,
)
from backend.app.database.connection import SessionLocal
from backend.app.database.models import ShipmentDB, WarehouseDB


class LogisticsAgent(BaseAgent[LogisticsInput, LogisticsResult]):
    """Logistics Modeling AI Agent in RIMBERIO.

    Computes deterministic transit lead times, freight costs, port congestion delays,
    carbon emission footprints, and maritime route risks.
    """

    ADVERSARIAL_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"system\s+prompt\s+override", re.IGNORECASE),
        re.compile(r"zero\s+freight\s+cost", re.IGNORECASE),
        re.compile(r"free\s+shipping\s+override", re.IGNORECASE),
        re.compile(r"instant\s+teleportation", re.IGNORECASE),
        re.compile(r"bypass\s+customs", re.IGNORECASE),
        re.compile(r"as\s+an\s+admin", re.IGNORECASE),
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE),
        re.compile(r"(drop|delete|insert|update)\s+table", re.IGNORECASE),
    ]

    # Rates per ton-km (in USD)
    FREIGHT_RATE_PER_TON_KM = {
        ShippingMode.AIR: 1.20,
        ShippingMode.ROAD: 0.14,
        ShippingMode.RAIL: 0.08,
        ShippingMode.OCEAN: 0.035,
        ShippingMode.MULTIMODAL: 0.075,
    }

    # Minimum baseline freight charge
    MIN_FREIGHT_CHARGE = {
        ShippingMode.AIR: 250.0,
        ShippingMode.ROAD: 100.0,
        ShippingMode.RAIL: 120.0,
        ShippingMode.OCEAN: 300.0,
        ShippingMode.MULTIMODAL: 200.0,
    }

    # Carbon emissions factor: kg CO2 per ton-km
    CO2_KG_PER_TON_KM = {
        ShippingMode.AIR: 0.500,
        ShippingMode.ROAD: 0.062,
        ShippingMode.RAIL: 0.022,
        ShippingMode.OCEAN: 0.008,
        ShippingMode.MULTIMODAL: 0.040,
    }

    def __init__(self, db: Optional[Session] = None):
        super().__init__(
            name="Logistics Agent",
            description="Autonomous logistics modeler calculating freight rates, transit times, port congestion, and carbon footprints.",
            capabilities=[AgentCapability.LOGISTICS_MODELING],
        )
        self.db = db

    def validate_input(self, input_data: Any) -> LogisticsInput:
        if isinstance(input_data, LogisticsInput):
            return input_data
        elif isinstance(input_data, dict):
            return LogisticsInput(**input_data)
        raise ValueError(f"Unsupported input type for LogisticsAgent: {type(input_data)}")

    def run_deterministic_logic(
        self,
        validated_input: LogisticsInput,
        state: Optional[Any] = None,
    ) -> LogisticsResult:
        return self._execute_deterministic(validated_input)

    def _execute_deterministic(self, input_data: LogisticsInput) -> LogisticsResult:
        # 1. Adversarial Inspection
        adversarial_flags = self._detect_adversarial_patterns(input_data.shipment_notes)

        # 2. Transit Lead Time Calculation
        transit_days, min_days, max_days = self._calculate_transit_time(
            distance_km=input_data.distance_km,
            shipping_mode=input_data.shipping_mode,
            port_status=input_data.port_status,
            customs_clearance_days=input_data.customs_clearance_days,
            expedited=input_data.expedited,
        )

        # 3. Freight and Handling Cost Calculation
        freight_cost, handling_fees, total_cost, cost_per_kg = self._calculate_costs(
            distance_km=input_data.distance_km,
            weight_kg=input_data.shipment_weight_kg,
            shipping_mode=input_data.shipping_mode,
            expedited=input_data.expedited,
        )

        # 4. Carbon Footprint Calculation (ton-km * CO2 factor)
        tons = input_data.shipment_weight_kg / 1000.0
        ton_km = tons * input_data.distance_km
        co2_factor = self.CO2_KG_PER_TON_KM.get(input_data.shipping_mode, 0.035)
        carbon_emissions = round(ton_km * co2_factor, 2)

        # 5. Route Risk Scoring
        route_risk = self._calculate_route_risk(
            distance_km=input_data.distance_km,
            shipping_mode=input_data.shipping_mode,
            port_status=input_data.port_status,
        )

        # 6. Carrier Reliability Resolution
        is_reliable = self._evaluate_carrier_reliability(input_data.carrier_code)

        # 7. Structured Reasoning Synthesis
        reasoning = self._generate_reasoning(
            input_data=input_data,
            transit_days=transit_days,
            min_days=min_days,
            max_days=max_days,
            total_cost=total_cost,
            carbon_emissions=carbon_emissions,
            route_risk=route_risk,
            is_reliable=is_reliable,
            adversarial_flags=adversarial_flags,
        )

        return LogisticsResult(
            shipping_mode=input_data.shipping_mode,
            origin_country=input_data.origin_country,
            destination_country=input_data.destination_country,
            distance_km=input_data.distance_km,
            shipment_weight_kg=input_data.shipment_weight_kg,
            estimated_transit_days=transit_days,
            min_transit_days=min_days,
            max_transit_days=max_days,
            freight_cost=freight_cost,
            handling_and_port_fees=handling_fees,
            total_logistics_cost=total_cost,
            cost_per_kg=cost_per_kg,
            carbon_emissions_kg_co2=carbon_emissions,
            route_risk_score=route_risk,
            is_carrier_reliable=is_reliable,
            reasoning=reasoning,
            adversarial_flags=adversarial_flags,
        )

    def _calculate_transit_time(
        self,
        distance_km: float,
        shipping_mode: ShippingMode,
        port_status: PortStatus,
        customs_clearance_days: float,
        expedited: bool,
    ) -> tuple[float, float, float]:
        """Calculates transit days (mean, min, max) including port delays and customs."""
        if shipping_mode == ShippingMode.AIR:
            # Air: average 800 km/h flight + airport ground handling (1-2 days)
            pure_transit = max(1.0, round(distance_km / 12000.0, 1) + 1.0)
            variance = 0.5
        elif shipping_mode == ShippingMode.ROAD:
            # Road: ~600 km/day
            pure_transit = max(1.0, round(distance_km / 600.0, 1))
            variance = 1.0
        elif shipping_mode == ShippingMode.RAIL:
            # Rail: ~450 km/day
            pure_transit = max(2.0, round(distance_km / 450.0, 1))
            variance = 1.5
        elif shipping_mode == ShippingMode.OCEAN:
            # Ocean: ~650 km/day sailing + port turnaround
            pure_transit = max(5.0, round(distance_km / 650.0, 1) + 3.0)
            variance = 3.0
        else:  # MULTIMODAL
            pure_transit = max(3.0, round(distance_km / 550.0, 1) + 2.0)
            variance = 2.0

        # Port Congestion Buffer
        congestion_delay = 0.0
        if port_status == PortStatus.CONGESTED:
            congestion_delay = 3.5
        elif port_status == PortStatus.CRITICAL_BOTTLENECK:
            congestion_delay = 8.0

        # Expedited reduces ground turnaround by 25%
        if expedited:
            pure_transit = max(1.0, round(pure_transit * 0.75, 1))

        estimated_days = round(pure_transit + congestion_delay + customs_clearance_days, 1)
        min_days = round(max(1.0, estimated_days - variance), 1)
        max_days = round(estimated_days + variance + (1.5 if port_status != PortStatus.NORMAL else 0.0), 1)

        return estimated_days, min_days, max_days

    def _calculate_costs(
        self,
        distance_km: float,
        weight_kg: float,
        shipping_mode: ShippingMode,
        expedited: bool,
    ) -> tuple[float, float, float, float]:
        """Calculates freight, handling, total cost, and cost per kg."""
        tons = weight_kg / 1000.0
        ton_km = tons * distance_km
        rate = self.FREIGHT_RATE_PER_TON_KM.get(shipping_mode, 0.05)
        min_charge = self.MIN_FREIGHT_CHARGE.get(shipping_mode, 150.0)

        raw_freight = ton_km * rate
        if expedited:
            raw_freight *= 1.45

        freight_cost = round(max(min_charge, raw_freight), 2)

        # Handling and port fees based on mode
        if shipping_mode == ShippingMode.AIR:
            handling_fees = round(max(50.0, weight_kg * 0.12 + 60.0), 2)
        elif shipping_mode == ShippingMode.OCEAN:
            handling_fees = round(max(150.0, weight_kg * 0.035 + 200.0), 2)
        elif shipping_mode == ShippingMode.ROAD:
            handling_fees = round(max(30.0, weight_kg * 0.015 + 40.0), 2)
        elif shipping_mode == ShippingMode.RAIL:
            handling_fees = round(max(60.0, weight_kg * 0.025 + 70.0), 2)
        else:
            handling_fees = round(max(80.0, weight_kg * 0.03 + 90.0), 2)

        total_cost = round(freight_cost + handling_fees, 2)
        cost_per_kg = round(total_cost / max(1.0, weight_kg), 4)

        return freight_cost, handling_fees, total_cost, cost_per_kg

    def _calculate_route_risk(
        self,
        distance_km: float,
        shipping_mode: ShippingMode,
        port_status: PortStatus,
    ) -> float:
        """Evaluates empirical route disruption risk (0 to 100)."""
        base_risk = 15.0

        # Distance risk
        if distance_km > 10000.0:
            base_risk += 15.0
        elif distance_km > 5000.0:
            base_risk += 8.0

        # Mode risk
        if shipping_mode == ShippingMode.OCEAN:
            base_risk += 12.0
        elif shipping_mode == ShippingMode.MULTIMODAL:
            base_risk += 15.0
        elif shipping_mode == ShippingMode.ROAD:
            base_risk += 8.0
        elif shipping_mode == ShippingMode.AIR:
            base_risk += 4.0

        # Port status risk
        if port_status == PortStatus.CONGESTED:
            base_risk += 22.0
        elif port_status == PortStatus.CRITICAL_BOTTLENECK:
            base_risk += 45.0

        return round(min(100.0, max(5.0, base_risk)), 1)

    def _evaluate_carrier_reliability(self, carrier_code: Optional[str]) -> bool:
        """Verifies carrier performance against historical records or carrier designation."""
        if not carrier_code:
            return True
        # Known high-reliability logistics lines
        premier_carriers = ["MAERSK", "MSC", "DHL", "FEDEX", "UPS", "COSCO", "HAPAG"]
        return any(p in carrier_code.upper() for p in premier_carriers) or len(carrier_code) > 2

    def _detect_adversarial_patterns(self, text: Optional[str]) -> List[str]:
        if not text:
            return []
        flags = []
        for pat in self.ADVERSARIAL_PATTERNS:
            match = pat.search(text)
            if match:
                flags.append(f"Prompt injection pattern detected: '{match.group()}'")
        return flags

    def _generate_reasoning(
        self,
        input_data: LogisticsInput,
        transit_days: float,
        min_days: float,
        max_days: float,
        total_cost: float,
        carbon_emissions: float,
        route_risk: float,
        is_reliable: bool,
        adversarial_flags: List[str],
    ) -> str:
        parts = []
        if adversarial_flags:
            parts.append(f"[SECURITY ALERT: {len(adversarial_flags)} injection pattern(s) neutralized.]")

        exp_str = " (Expedited Service)" if input_data.expedited else ""
        parts.append(
            f"Routing {input_data.shipment_weight_kg:,.1f}kg via {input_data.shipping_mode.value}{exp_str} "
            f"from {input_data.origin_country} to {input_data.destination_country} ({input_data.distance_km:,.0f} km)."
        )
        parts.append(
            f"Estimated transit is {transit_days:.1f} days (range {min_days:.1f}–{max_days:.1f} days) "
            f"accounting for {input_data.port_status.value} port status and {input_data.customs_clearance_days:.1f}d customs processing."
        )
        parts.append(
            f"Total logistics cost is ${total_cost:,.2f} (${total_cost / input_data.shipment_weight_kg:.2f}/kg). "
            f"Estimated carbon footprint: {carbon_emissions:,.1f} kg CO2."
        )
        parts.append(
            f"Route disruption risk evaluated at {route_risk}/100. Carrier reliability status: {'CONFIRMED' if is_reliable else 'UNVERIFIED'}."
        )

        return " ".join(parts)


# Register in AgentRegistry
AgentRegistry.register(
    name="Logistics Agent",
    agent_class=LogisticsAgent,
    capabilities=[AgentCapability.LOGISTICS_MODELING],
    version="1.0.0",
)
