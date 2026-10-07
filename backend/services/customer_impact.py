from typing import List, Dict, Any
from backend.models.schemas import ImpactedCustomerOrder, BatchNotificationRequest, NotificationDispatchResult
from backend.services.customization_store import customization_store
from backend.services.data_manager import data_manager
from backend.agents.customer_impact_agent import CustomerImpactAgentModel

class CustomerImpactEngine:
    """
    Customer Impact Engine powered by CustomerImpactAgentModel.
    Audits active customer orders from DynamicDataManager and generates personalized advisories.
    """

    def __init__(self):
        self.impact_model = CustomerImpactAgentModel()

    def get_impacted_orders(self) -> List[ImpactedCustomerOrder]:
        raw_orders = data_manager.get_orders()
        evaluated = self.impact_model.evaluate_orders_impact(raw_orders, delay_days=6)
        
        results = []
        for o in evaluated["impacted_orders"]:
            results.append(
                ImpactedCustomerOrder(
                    order_id=o["order_id"],
                    customer_name=o["customer_name"],
                    customer_tier=o["customer_tier"],
                    contact_email=o["contact_email"],
                    sku_code=o["sku_code"],
                    quantity=o["quantity"],
                    promised_eta=o["promised_eta"],
                    revised_eta=o["revised_eta"],
                    delay_days=o["delay_days"],
                    sla_penalty_exposure=o["sla_penalty_exposure"],
                    status=o["status"]
                )
            )
        return results

    def dispatch_batch_notifications(self, req: BatchNotificationRequest) -> NotificationDispatchResult:
        profile = customization_store.get_profile()
        tmpl = profile.notifications

        raw_orders = data_manager.get_orders()
        dispatched = []
        sample_subject = ""
        sample_body = ""

        for order in raw_orders:
            if order["order_id"] in req.order_ids:
                order["status"] = "ADVISORY_DISPATCHED"
                dispatched.append(order["order_id"])

                # Render dynamic template
                rendered_subject = tmpl.email_subject.format(order_id=order["order_id"])
                rendered_body = tmpl.email_body.format(
                    customer_name=order["customer_name"],
                    order_id=order["order_id"],
                    sku_name="Micro-Capacitor SKU-MC-772",
                    disruption_reason=req.disruption_reason or "global maritime route transit delay",
                    revised_delivery_date=order.get("revised_eta", "2026-10-20"),
                    delay_days=order.get("delay_days", 6)
                )

                if not sample_subject:
                    sample_subject = rendered_subject
                    sample_body = rendered_body

        return NotificationDispatchResult(
            total_dispatched=len(dispatched),
            dispatched_orders=dispatched,
            sample_rendered_subject=sample_subject or "Notice Dispatched",
            sample_rendered_message=sample_body or "Notice details dispatched successfully.",
            status="SUCCESS"
        )

customer_impact_engine = CustomerImpactEngine()
