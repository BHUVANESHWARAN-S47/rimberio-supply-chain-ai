import re
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.agents.base import BaseAgent
from backend.app.agents.registry import AgentRegistry
from backend.app.schemas.common import AgentCapability
from backend.app.schemas.customer_impact import (
    CustomerImpactEvaluationRequest,
    CustomerImpactEvaluationResponse,
    CustomerOrderImpact,
    CustomerNotificationPayload,
    CustomerPriorityTier,
    CustomerImpactLevel,
)
from backend.app.database.models import (
    CustomerDB,
    CustomerOrderDB,
    CustomerImpactDB,
    CustomerNotificationDB,
)
from backend.app.core.llm import llm_service


class CustomerImpactAgent(BaseAgent[CustomerImpactEvaluationRequest, CustomerImpactEvaluationResponse]):
    """Downstream Customer Impact & SLA Exposure Assessment AI Agent.

    Evaluates delivery delay propagation, contractual SLA breach penalties,
    customer churn vulnerabilities, and triggers automated advisory dispatches.
    Zero-hallucination deterministic mathematics with Groq LLaMA narrative synthesis.
    """

    ADVERSARIAL_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"waive\s+(all\s+)?sla(\s+penalties)?", re.IGNORECASE),
        re.compile(r"set\s+churn(\s+risk)?\s+to\s+0", re.IGNORECASE),
        re.compile(r"zero\s+penalty\s+override", re.IGNORECASE),
        re.compile(r"bypass\s+customer\s+audit", re.IGNORECASE),
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE),
        re.compile(r"(drop|delete|insert|update)\s+table", re.IGNORECASE),
    ]

    TIER_RATES = {
        "CRITICAL": {"daily_penalty_rate": 0.015, "churn_weight": 0.85},
        "Enterprise Tier 1": {"daily_penalty_rate": 0.015, "churn_weight": 0.85},
        "HIGH": {"daily_penalty_rate": 0.008, "churn_weight": 0.50},
        "Commercial High-Volume": {"daily_penalty_rate": 0.008, "churn_weight": 0.50},
        "STANDARD": {"daily_penalty_rate": 0.004, "churn_weight": 0.25},
        "Standard Commercial": {"daily_penalty_rate": 0.004, "churn_weight": 0.25},
    }

    def __init__(self, db: Optional[Session] = None):
        super().__init__(
            name="Customer Impact Agent",
            description="Audits downstream client order delivery delays, SLA liability exposure, and churn risks.",
            capabilities=[AgentCapability.CUSTOMER_IMPACT_ANALYSIS],
        )
        self.db = db

    def validate_input(self, input_data: Any) -> CustomerImpactEvaluationRequest:
        if isinstance(input_data, CustomerImpactEvaluationRequest):
            return input_data
        elif isinstance(input_data, dict):
            return CustomerImpactEvaluationRequest(**input_data)
        raise ValueError(f"Unsupported input type for CustomerImpactAgent: {type(input_data)}")

    def run_deterministic_logic(
        self,
        validated_input: CustomerImpactEvaluationRequest,
        state: Optional[Any] = None,
    ) -> CustomerImpactEvaluationResponse:
        return self._execute_deterministic(validated_input)

    def _execute_deterministic(
        self,
        req: CustomerImpactEvaluationRequest,
    ) -> CustomerImpactEvaluationResponse:
        orders_to_audit = self._gather_orders(req)
        delay_days = max(0, req.expected_delay_days)
        fill_drop = min(1.0, max(0.0, req.fill_rate_reduction))

        impacted_orders: List[CustomerOrderImpact] = []
        notifications: List[CustomerNotificationPayload] = []

        total_penalty = 0.0
        total_units = 0
        total_rev_at_risk = 0.0
        critical_count = 0
        high_count = 0

        for ord_info in orders_to_audit:
            order_id = str(ord_info.get("order_id", f"ORD-{uuid.uuid4().hex[:6].upper()}"))
            customer_id = str(ord_info.get("customer_id", f"CUST-{uuid.uuid4().hex[:6].upper()}"))
            customer_name = ord_info.get("customer_name", "Enterprise Client")
            raw_tier = str(ord_info.get("customer_tier", "STANDARD")).upper()

            # Normalize tier
            if "CRIT" in raw_tier or "TIER 1" in raw_tier or "ENTERPRISE" in raw_tier:
                tier = "CRITICAL"
            elif "HIGH" in raw_tier or "VOLUME" in raw_tier:
                tier = "HIGH"
            else:
                tier = "STANDARD"

            product_id = str(ord_info.get("product_id", "PROD-GENERIC"))
            qty = max(0, int(ord_info.get("quantity", 100)))
            unit_price = max(0.0, float(ord_info.get("unit_price", 100.0)))
            order_value = float(ord_info.get("order_value", qty * unit_price))
            if order_value <= 0.0 and qty > 0 and unit_price > 0.0:
                order_value = qty * unit_price

            promised_str = str(ord_info.get("promised_delivery_date") or ord_info.get("promised_eta") or date.today().isoformat())
            try:
                if "T" in promised_str:
                    promised_dt = datetime.fromisoformat(promised_str.replace("Z", "")).date()
                else:
                    promised_dt = date.fromisoformat(promised_str[:10])
                revised_dt = promised_dt + timedelta(days=delay_days)
                revised_str = revised_dt.isoformat()
            except Exception:
                revised_str = promised_str

            tier_meta = self.TIER_RATES.get(tier, self.TIER_RATES["STANDARD"])
            penalty_rate = tier_meta["daily_penalty_rate"]
            churn_weight = tier_meta["churn_weight"]

            # SLA penalty capped at order value
            raw_penalty = order_value * penalty_rate * delay_days
            penalty = round(min(order_value, raw_penalty), 2)

            # Churn risk score 0 to 100
            base_churn = (delay_days * 8.0 + fill_drop * 50.0) * churn_weight
            churn_score = round(min(100.0, max(0.0, base_churn)), 1)

            # Order revenue at risk
            if churn_score >= 60.0:
                rev_risk = order_value
            elif delay_days > 0 or fill_drop > 0:
                rev_risk = round(order_value * min(1.0, (churn_score / 100.0) + (penalty / (order_value + 1e-6))), 2)
            else:
                rev_risk = 0.0

            total_penalty += penalty
            total_units += qty
            total_rev_at_risk += rev_risk

            if churn_score >= 50.0 or (tier == "CRITICAL" and delay_days > 0):
                critical_count += 1
            elif churn_score >= 25.0 or (tier == "HIGH" and delay_days > 0):
                high_count += 1

            impact_rec = CustomerOrderImpact(
                order_id=order_id,
                customer_id=customer_id,
                customer_name=customer_name,
                customer_tier=tier,
                product_id=product_id,
                quantity=qty,
                order_value=round(order_value, 2),
                promised_delivery_date=str(promised_str),
                revised_delivery_date=revised_str,
                delay_days=delay_days,
                daily_penalty_rate=penalty_rate,
                sla_penalty_exposure=penalty,
                churn_risk_score=churn_score,
                status="CRITICAL_EXPOSURE" if churn_score >= 60 else "DELAY_ADVISORY" if delay_days > 0 else "NORMAL",
            )
            impacted_orders.append(impact_rec)

            # Dispatch notification if at risk
            if delay_days > 0 or fill_drop > 0:
                severity = "URGENT" if (churn_score >= 60.0 or tier == "CRITICAL") else "WARNING" if delay_days >= 3 else "INFO"
                notif = CustomerNotificationPayload(
                    customer_id=customer_id,
                    customer_name=customer_name,
                    notification_type="SUPPLY_DISRUPTION_ADVISORY",
                    title=f"Delivery Timeline Update: Order {order_id} ({customer_name})",
                    message=(
                        f"Notice for {customer_name}: Product line {product_id} is projected to experience a {delay_days}-day "
                        f"transit adjustment (Revised ETA: {revised_str}). Estimated SLA mitigation: ${penalty:,.2f}."
                    ),
                    severity=severity,
                )
                notifications.append(notif)

        # Categorize overall impact level
        if critical_count > 0 or total_rev_at_risk >= 75000 or total_penalty >= 20000:
            overall_level = CustomerImpactLevel.CRITICAL.value
        elif high_count > 0 or total_rev_at_risk >= 25000 or total_penalty >= 5000:
            overall_level = CustomerImpactLevel.HIGH.value
        elif total_penalty > 0 or total_rev_at_risk > 0:
            overall_level = CustomerImpactLevel.MEDIUM.value
        elif delay_days > 0:
            overall_level = CustomerImpactLevel.LOW.value
        else:
            overall_level = CustomerImpactLevel.NONE.value

        # Persist to database if Session provided
        if self.db and req.simulation_run_id:
            self._persist_impacts(req, impacted_orders, notifications, overall_level)

        summary = self._generate_executive_summary(
            audited_count=len(impacted_orders),
            affected_units=total_units,
            penalty_exposure=total_penalty,
            rev_at_risk=total_rev_at_risk,
            critical_count=critical_count,
            delay_days=delay_days,
            overall_level=overall_level,
        )

        return CustomerImpactEvaluationResponse(
            total_orders_audited=len(impacted_orders),
            total_affected_units=total_units,
            total_revenue_at_risk=round(total_rev_at_risk, 2),
            total_sla_penalty_exposure=round(total_penalty, 2),
            overall_impact_level=overall_level,
            critical_orders_count=critical_count,
            high_orders_count=high_count,
            impacted_orders=impacted_orders,
            generated_notifications=notifications,
            executive_summary=summary,
        )

    def _gather_orders(self, req: CustomerImpactEvaluationRequest) -> List[Dict[str, Any]]:
        orders: List[Dict[str, Any]] = []

        # 1. Direct request orders
        if req.orders:
            for o in req.orders:
                orders.append(o)

        # 2. Database orders
        if req.include_db_orders and self.db:
            try:
                query = self.db.query(CustomerOrderDB).join(CustomerDB)
                if req.product_id:
                    query = query.filter(CustomerOrderDB.product_id == req.product_id)
                db_orders = query.limit(50).all()

                for dbo in db_orders:
                    cust = dbo.customer
                    tier_str = cust.priority if cust and cust.priority else "STANDARD"
                    cust_name = cust.name if cust else "Client Partner"
                    orders.append({
                        "order_id": str(dbo.id),
                        "customer_id": str(dbo.customer_id),
                        "customer_name": cust_name,
                        "customer_tier": tier_str,
                        "product_id": str(dbo.product_id),
                        "quantity": dbo.quantity,
                        "unit_price": dbo.unit_price,
                        "order_value": dbo.total_amount,
                        "promised_delivery_date": dbo.promised_delivery_date.isoformat() if dbo.promised_delivery_date else date.today().isoformat(),
                    })
            except Exception:
                pass

        # 3. Fallback baseline if empty
        if not orders:
            orders.append({
                "order_id": "ORD-SAMPLE-01",
                "customer_id": "CUST-ENT-001",
                "customer_name": "Apex Global Industries",
                "customer_tier": "CRITICAL",
                "product_id": req.product_id or "PROD-A",
                "quantity": 1000,
                "unit_price": 120.0,
                "order_value": 120000.0,
                "promised_delivery_date": date.today().isoformat(),
            })

        return orders

    def _persist_impacts(
        self,
        req: CustomerImpactEvaluationRequest,
        impacted_orders: List[CustomerOrderImpact],
        notifications: List[CustomerNotificationPayload],
        overall_level: str,
    ):
        try:
            sim_id = uuid.UUID(req.simulation_run_id) if isinstance(req.simulation_run_id, str) else req.simulation_run_id
            for imp in impacted_orders:
                try:
                    cust_uuid = uuid.UUID(imp.customer_id)
                except Exception:
                    cust_uuid = uuid.uuid4()
                try:
                    ord_uuid = uuid.UUID(imp.order_id)
                except Exception:
                    ord_uuid = None
                try:
                    prod_uuid = uuid.UUID(imp.product_id)
                except Exception:
                    prod_uuid = uuid.uuid4()

                db_impact = CustomerImpactDB(
                    simulation_run_id=sim_id,
                    customer_id=cust_uuid,
                    affected_order_id=ord_uuid,
                    supplier_id=uuid.UUID(req.supplier_id) if req.supplier_id else None,
                    affected_product_id=prod_uuid,
                    expected_delay_days=imp.delay_days,
                    availability_change=-round(imp.churn_risk_score * 0.1, 2),
                    service_level_change=-round(imp.delay_days * 1.5, 2),
                    revenue_at_risk=imp.order_value if imp.churn_risk_score >= 50 else imp.sla_penalty_exposure,
                    impact_level=imp.status,
                    reasoning=f"Delay of {imp.delay_days} days causes SLA liability of ${imp.sla_penalty_exposure:,.2f}",
                )
                self.db.add(db_impact)
            self.db.commit()
        except Exception:
            if self.db:
                self.db.rollback()

    def _generate_executive_summary(
        self,
        audited_count: int,
        affected_units: int,
        penalty_exposure: float,
        rev_at_risk: float,
        critical_count: int,
        delay_days: int,
        overall_level: str,
    ) -> str:
        deterministic_summary = (
            f"Customer Impact Audit ({overall_level}): Evaluated {audited_count} order line(s) totaling {affected_units:,} units. "
            f"Projected transit delay of {delay_days} days produces ${penalty_exposure:,.2f} in contractual SLA penalty liabilities "
            f"and puts ${rev_at_risk:,.2f} in client revenue at risk. {critical_count} critical client account(s) require priority advisory."
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are the RIMBERIO Customer Impact AI Agent. "
                    "Draft a concise, professional supply chain executive summary. "
                    "Do NOT recalculate or contradict the provided numbers."
                ),
            },
            {
                "role": "user",
                "content": f"Synthesize this operational customer impact analysis:\n{deterministic_summary}",
            },
        ]
        return llm_service.generate_completion(
            messages=messages,
            fallback_response=deterministic_summary,
            max_tokens=300,
        )


AgentRegistry.register("customer_impact_agent", CustomerImpactAgent)
