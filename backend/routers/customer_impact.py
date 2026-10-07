from typing import List
from fastapi import APIRouter
from backend.models.schemas import ImpactedCustomerOrder, BatchNotificationRequest, NotificationDispatchResult
from backend.services.customer_impact import customer_impact_engine

router = APIRouter(prefix="/api/customer-impact", tags=["Customer Impact & Automated Notice Dispatch"])

@router.get("/orders", response_model=List[ImpactedCustomerOrder])
def list_impacted_orders():
    """List customer orders impacted by active route/supplier disruption events."""
    return customer_impact_engine.get_impacted_orders()

@router.post("/notify/batch", response_model=NotificationDispatchResult)
def dispatch_batch_notifications(req: BatchNotificationRequest):
    """Render notification templates with live order variables and dispatch to affected customers."""
    return customer_impact_engine.dispatch_batch_notifications(req)
