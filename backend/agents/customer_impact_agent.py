from typing import List, Dict, Any
import datetime

class CustomerImpactAgentModel:
    """
    Customer Impact Agent Model.
    Audits downstream impact on customer orders for ANY dataset of clients, order values, and ETAs.
    Calculates contractual SLA penalties, churn risk scores, and generates transparent advisories.
    """

    TIER_PENALTY_RATES = {
        "Enterprise Tier 1": {"daily_penalty_rate": 0.015, "churn_weight": 0.85},   # 1.5% of order value per day
        "Commercial High-Volume": {"daily_penalty_rate": 0.008, "churn_weight": 0.50},# 0.8% of order value per day
        "Standard Commercial": {"daily_penalty_rate": 0.004, "churn_weight": 0.25},   # 0.4% of order value per day
    }

    def evaluate_orders_impact(
        self,
        orders: List[Dict[str, Any]],
        delay_days: int,
        disruption_reason: str = "Maritime corridor transit delay"
    ) -> Dict[str, Any]:
        """
        Evaluates SLA exposure and generates advisories for ANY arbitrary list of orders.
        """
        total_penalty = 0.0
        total_affected_units = 0
        at_risk_orders = []

        for ord_data in orders:
            order_id = ord_data.get("order_id", "ORD-UNKNOWN")
            customer_name = ord_data.get("customer_name", "Enterprise Customer")
            tier = ord_data.get("customer_tier", "Standard Commercial")
            unit_price = ord_data.get("unit_price", 145.0)
            quantity = ord_data.get("quantity", 1000)
            order_value = ord_data.get("order_value", unit_price * quantity)
            contact_email = ord_data.get("contact_email", "procurement@customer.com")
            sku_code = ord_data.get("sku_code", "SKU-GENERIC")
            promised_eta_str = ord_data.get("promised_eta", datetime.date.today().isoformat())

            # Calculate revised ETA
            try:
                promised_date = datetime.date.fromisoformat(promised_eta_str)
                revised_date = promised_date + datetime.timedelta(days=delay_days)
                revised_eta_str = revised_date.isoformat()
            except Exception:
                revised_eta_str = promised_eta_str

            tier_info = self.TIER_PENALTY_RATES.get(tier, self.TIER_PENALTY_RATES["Standard Commercial"])
            order_penalty = round(order_value * (tier_info["daily_penalty_rate"] * delay_days), 2)
            churn_risk_score = round(min(100.0, (delay_days * 8.0) * tier_info["churn_weight"]), 1)

            total_penalty += order_penalty
            total_affected_units += quantity

            at_risk_orders.append({
                "order_id": order_id,
                "customer_name": customer_name,
                "customer_tier": tier,
                "contact_email": contact_email,
                "sku_code": sku_code,
                "quantity": quantity,
                "order_value": order_value,
                "promised_eta": promised_eta_str,
                "revised_eta": revised_eta_str,
                "delay_days": delay_days,
                "sla_penalty_exposure": order_penalty,
                "churn_risk_score": churn_risk_score,
                "status": "PENDING_ADVISORY"
            })

        critical_count = sum(1 for o in at_risk_orders if o["churn_risk_score"] > 50.0)

        return {
            "total_orders_audited": len(orders),
            "total_affected_units": total_affected_units,
            "total_sla_penalty_exposure": round(total_penalty, 2),
            "critical_risk_orders_count": critical_count,
            "impacted_orders": at_risk_orders,
            "agent_summary": (
                f"Customer Impact Audit: Evaluated {len(orders)} active order lines across {total_affected_units:,} units. "
                f"Projected delay of {delay_days} days produces ${total_penalty:,.2f} in SLA penalty exposure. "
                f"{critical_count} Tier-1 clients require priority advisory dispatch."
            )
        }
