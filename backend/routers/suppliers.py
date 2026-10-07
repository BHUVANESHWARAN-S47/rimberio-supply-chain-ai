from typing import List
from fastapi import APIRouter
from backend.models.schemas import SupplierProfile
from backend.services.decision_engine import decision_engine

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])

@router.get("", response_model=List[SupplierProfile])
def list_suppliers():
    """Retrieve all suppliers with real-time weighted composite scores calculated from active customization weights."""
    return decision_engine.get_all_suppliers()
