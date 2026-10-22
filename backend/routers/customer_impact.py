from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from backend.models.schemas import ImpactedCustomerOrder, BatchNotificationRequest, NotificationDispatchResult
from backend.services.customer_impact import customer_impact_engine
from backend.services.data_manager import data_manager

router = APIRouter(prefix="/api/customer-impact", tags=["Customer Impact & Automated Notice Dispatch"])


@router.get("/orders", response_model=List[ImpactedCustomerOrder])
def list_impacted_orders():
    """List customer orders impacted by active route/supplier disruption events."""
    return customer_impact_engine.get_impacted_orders()


@router.post("/orders", response_model=Dict[str, Any])
def create_customer_order(order_data: Dict[str, Any]):
    """Add a new customer order to the active delivery ledger."""
    created = data_manager.add_order(order_data)
    return {"status": "SUCCESS", "message": f"Order {created.get('order_id')} created successfully.", "order": created}


@router.put("/orders/{order_id}", response_model=Dict[str, Any])
def update_customer_order(order_id: str, update_data: Dict[str, Any]):
    """Update an existing customer order."""
    updated = data_manager.update_order(order_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")
    return {"status": "SUCCESS", "message": f"Order {order_id} updated.", "order": updated}


@router.delete("/orders/{order_id}", response_model=Dict[str, Any])
def delete_customer_order(order_id: str):
    """Delete an order from the tracking system."""
    deleted = data_manager.delete_order(order_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")
    return {"status": "SUCCESS", "message": f"Order {order_id} deleted successfully."}


@router.post("/notify/batch", response_model=NotificationDispatchResult)
def dispatch_batch_notifications(req: BatchNotificationRequest):
    """Render notification templates with live order variables and dispatch to affected customers."""
    return customer_impact_engine.dispatch_batch_notifications(req)


@router.post("/notify/{order_id}")
def dispatch_single_notification(order_id: str, disruption_reason: str = "Maritime corridor transit adjustment"):
    """Dispatch notice for a specific order."""
    req = BatchNotificationRequest(order_ids=[order_id], disruption_reason=disruption_reason)
    return customer_impact_engine.dispatch_batch_notifications(req)
