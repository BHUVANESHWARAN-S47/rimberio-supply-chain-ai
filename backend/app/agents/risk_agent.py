import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.agents.base import BaseAgent
from backend.app.agents.registry import AgentRegistry
from backend.app.schemas.common import AgentCapability, RiskLevel
from backend.app.schemas.risk import RiskInput, RiskAssessmentResult, RiskCategory
from backend.app.database.connection import SessionLocal
from backend.app.database.models import SupplierDB, RiskEventDB
from backend.app.core.llm import llm_service


class RiskAgent(BaseAgent[RiskInput, RiskAssessmentResult]):
    """Enterprise Supply Chain Risk Assessment AI Agent in RIMBERIO.

    Computes deterministic multi-factor operational, financial, dependency,
    and geopolitical vulnerability metrics with Groq LLaMA reasoning integration.
    """

    ADVERSARIAL_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"system\s+prompt\s+override", re.IGNORECASE),
        re.compile(r"set\s+risk\s+to\s+0", re.IGNORECASE),
        re.compile(r"zero\s+risk\s+override", re.IGNORECASE),
        re.compile(r"classify\s+as\s+no\s+risk", re.IGNORECASE),
        re.compile(r"bypass\s+risk\s+checks", re.IGNORECASE),
        re.compile(r"as\s+an\s+admin", re.IGNORECASE),
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE),
        re.compile(r"(drop|delete|insert|update)\s+table", re.IGNORECASE),
    ]

    HIGH_RISK_REGIONS = ["WARZONE", "SANCTIONED", "EMBARGO", "CHOKEPOINT"]

    def __init__(self, db: Optional[Session] = None):
        super().__init__(
            name="Risk Agent",
            description="Autonomous risk evaluator assessing operational reliability, solvency, single-source exposure, and disruptions.",
            capabilities=[AgentCapability.RISK_ASSESSMENT],
        )
        self.db = db

    def validate_input(self, input_data: Any) -> RiskInput:
        if isinstance(input_data, RiskInput):
            return input_data
        elif isinstance(input_data, dict):
            return RiskInput(**input_data)
        raise ValueError(f"Unsupported input type for RiskAgent: {type(input_data)}")

    def run_deterministic_logic(
        self,
        validated_input: RiskInput,
        state: Optional[Any] = None,
    ) -> RiskAssessmentResult:
        return self._execute_deterministic(validated_input)

    def _execute_deterministic(self, input_data: RiskInput) -> RiskAssessmentResult:
        # 1. Adversarial Inspection
        adversarial_flags = self._detect_adversarial_patterns(input_data.analyst_notes)

        # 2. Category Risk Calculations (0-100 scales)
        # Operational Risk: on-time rate and defect rate
        ot_penalty = max(0.0, (100.0 - input_data.on_time_delivery_rate) * 1.5)
        defect_penalty = min(50.0, input_data.quality_defect_rate * 1500.0)
        operational_risk = round(min(100.0, ot_penalty + defect_penalty), 1)

        # Financial Risk: credit score inverse
        credit_score = input_data.financial_credit_score if input_data.financial_credit_score is not None else 80.0
        financial_risk = round(max(0.0, min(100.0, 100.0 - credit_score)), 1)

        # Dependency Risk: single source + spend concentration
        single_source_penalty = 45.0 if input_data.single_source else 10.0
        spend_penalty = min(45.0, input_data.spend_share_pct * 90.0)
        dependency_risk = round(min(100.0, single_source_penalty + spend_penalty), 1)

        # Geopolitical & Disruption Risk: historical events + high risk zones
        geo_base = 35.0 if any(r in input_data.country.upper() for r in self.HIGH_RISK_REGIONS) else 15.0
        disruption_penalty = min(50.0, input_data.disruption_event_history_count * 15.0)
        geopolitical_risk = round(min(100.0, geo_base + disruption_penalty), 1)

        # Climate Exposure Risk
        climate_risk = round(input_data.climate_exposure_score or 20.0, 1)

        # Compliance Risk
        compliance_risk = 15.0

        category_scores = {
            RiskCategory.OPERATIONAL.value: operational_risk,
            RiskCategory.FINANCIAL.value: financial_risk,
            RiskCategory.DEPENDENCY.value: dependency_risk,
            RiskCategory.GEOPOLITICAL.value: geopolitical_risk,
            RiskCategory.CLIMATE.value: climate_risk,
            RiskCategory.COMPLIANCE.value: compliance_risk,
        }

        # 3. Weighted Composite Risk Score
        composite_score = round(
            (operational_risk * 0.30)
            + (dependency_risk * 0.25)
            + (financial_risk * 0.20)
            + (geopolitical_risk * 0.15)
            + (climate_risk * 0.10),
            1,
        )

        # 4. Risk Level Categorization
        if composite_score < 25.0:
            risk_level = RiskLevel.LOW
        elif composite_score < 50.0:
            risk_level = RiskLevel.MEDIUM
        elif composite_score < 75.0:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL

        # 5. Key Risk Drivers
        drivers: List[str] = []
        if input_data.single_source:
            drivers.append("Single-source vulnerability: No secondary qualified supplier.")
        if input_data.spend_share_pct > 0.30:
            drivers.append(f"High portfolio spend concentration ({input_data.spend_share_pct*100:.1f}%).")
        if operational_risk > 40.0:
            drivers.append(f"Elevated operational failure hazard (on-time: {input_data.on_time_delivery_rate:.1f}%).")
        if financial_risk > 40.0:
            drivers.append(f"Weak supplier solvency index (credit: {credit_score:.0f}/100).")
        if input_data.disruption_event_history_count > 0:
            drivers.append(f"Past disruption history: {input_data.disruption_event_history_count} incidents logged.")

        # 6. Mitigation Recommendations
        recommendations: List[str] = []
        if input_data.single_source:
            recommendations.append("Initiate RFQ qualification for alternate second-source vendors immediately.")
        if input_data.spend_share_pct > 0.30:
            recommendations.append("Cap order allocation to 25% max category volume across quarterly procurement.")
        if operational_risk > 35.0:
            recommendations.append("Expand buffer safety stock from 14 days to 25 days coverage.")
        if financial_risk > 35.0:
            recommendations.append("Require letters of credit and enforce strict milestone delivery inspections.")

        if not recommendations:
            recommendations.append("Maintain standard quarterly SLA performance monitoring.")

        # 7. Confidence & Reasoning
        confidence = round(max(0.70, min(0.98, 0.95 - (composite_score / 500.0))), 2)
        reasoning = self._generate_reasoning(
            input_data=input_data,
            composite_score=composite_score,
            risk_level=risk_level,
            drivers=drivers,
            recommendations=recommendations,
            adversarial_flags=adversarial_flags,
        )

        return RiskAssessmentResult(
            supplier_id=input_data.supplier_id,
            composite_risk_score=composite_score,
            risk_level=risk_level,
            category_scores=category_scores,
            key_risk_drivers=drivers,
            mitigation_recommendations=recommendations,
            is_single_source_hazard=input_data.single_source,
            confidence=confidence,
            reasoning=reasoning,
            adversarial_flags=adversarial_flags,
        )

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
        input_data: RiskInput,
        composite_score: float,
        risk_level: RiskLevel,
        drivers: List[str],
        recommendations: List[str],
        adversarial_flags: List[str],
    ) -> str:
        parts = []
        if adversarial_flags:
            parts.append(f"[SECURITY ALERT: {len(adversarial_flags)} injection pattern(s) neutralized.]")

        sup_name = input_data.supplier_name or input_data.supplier_id
        parts.append(
            f"Evaluated comprehensive supply-chain exposure for {sup_name} ({input_data.country}). "
            f"Composite risk score is {composite_score}/100, categorized as {risk_level.value}."
        )

        if drivers:
            parts.append(f"Primary risk drivers: {' '.join(drivers)}")
        else:
            parts.append("Operational, financial, and geographical metrics demonstrate healthy baseline parameters.")

        parts.append(f"Recommended mitigation: {recommendations[0]}")
        return " ".join(parts)


# Register in AgentRegistry
AgentRegistry.register(
    name="Risk Agent",
    agent_class=RiskAgent,
    capabilities=[AgentCapability.RISK_ASSESSMENT],
    version="1.0.0",
)
