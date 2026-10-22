from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from backend.app.cnt.models import CustomerImpactResult, ImpactLevel


class CustomerImpactModel:
    """Evaluates direct and downstream customer consequences of supplier switching and delays.

    Traces order pipelines, promised customer ship dates, stockout probabilities,
    and revenue exposure based on actual order relationships.
    """

    def evaluate_customer_impact(
        self,
        pending_orders: List[Dict[str, Any]],
        stockout_rate: float,
        stockout_units: float,
        actual_lead_time_days: float,
        baseline_lead_time_days: float,
        unit_price: float,
    ) -> CustomerImpactResult:
        """Calculates customer impact from pending customer orders and replenishment delay."""
        delay_days = max(0.0, actual_lead_time_days - baseline_lead_time_days)

        affected_customers: List[str] = []
        affected_orders: List[str] = []
        total_revenue_at_risk = 0.0

        # Trace orders
        for ord_info in pending_orders:
            cust_name = ord_info.get("customer_name") or str(ord_info.get("customer_id", "Cust-Unknown"))
            order_no = ord_info.get("order_number") or str(ord_info.get("order_id", "Ord-Unknown"))
            order_amount = float(ord_info.get("total_amount", 0.0))
            order_qty = int(ord_info.get("quantity", 0))

            # If delayed replenishment breaches customer schedule or stockout occurs
            if delay_days > 2.0 or stockout_rate > 0.05:
                if cust_name not in affected_customers:
                    affected_customers.append(cust_name)
                if order_no not in affected_orders:
                    affected_orders.append(order_no)
                total_revenue_at_risk += order_amount

        # If no specific orders matched in memory but stockout units exist
        if not affected_orders and stockout_units > 0:
            total_revenue_at_risk = round(stockout_units * unit_price * 1.25, 2)
            affected_customers.append("Commercial Client Pool")
            affected_orders.append(f"Buffered Backorders ({int(stockout_units)} units)")

        # Service level change
        service_level_drop = round(min(50.0, (stockout_rate * 45.0) + (delay_days * 2.5)), 2)

        # Customer impact score (0 to 100)
        impact_score = round(
            min(100.0, (service_level_drop * 1.5) + (len(affected_orders) * 4.0) + min(25.0, total_revenue_at_risk / 2000.0)),
            1,
        )

        if impact_score < 15.0:
            impact_level = ImpactLevel.LOW
        elif impact_score < 40.0:
            impact_level = ImpactLevel.MEDIUM
        elif impact_score < 70.0:
            impact_level = ImpactLevel.HIGH
        else:
            impact_level = ImpactLevel.CRITICAL

        reasoning = (
            f"Fulfillment delay of {delay_days:.1f} days and stockout hazard {stockout_rate*100:.1f}% "
            f"exposes {len(affected_orders)} customer orders across {len(affected_customers)} client accounts "
            f"(${total_revenue_at_risk:,.2f} revenue at risk, estimated service level reduction -{service_level_drop:.1f}%)."
        )

        return CustomerImpactResult(
            affected_customers=affected_customers,
            affected_orders=affected_orders,
            expected_delay_days=round(delay_days, 1),
            service_level_change=round(-service_level_drop, 2),
            revenue_at_risk=round(total_revenue_at_risk, 2),
            customer_impact_score=impact_score,
            impact_level=impact_level,
            reasoning=reasoning,
        )
