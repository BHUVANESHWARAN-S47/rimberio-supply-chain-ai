from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from backend.models.schemas import SupplierProfile
from backend.services.decision_engine import decision_engine
from backend.services.data_manager import data_manager

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])


@router.get("", response_model=List[SupplierProfile])
def list_suppliers():
    """Retrieve all suppliers with real-time weighted composite scores."""
    return decision_engine.get_all_suppliers()


@router.post("", response_model=Dict[str, Any])
def create_supplier(supplier_data: Dict[str, Any]):
    """Create a new supplier record and store in the system database."""
    created = data_manager.add_supplier(supplier_data)
    return {"status": "SUCCESS", "message": f"Supplier {created.get('name')} created successfully.", "supplier": created}


@router.put("/{supplier_code}", response_model=Dict[str, Any])
def update_supplier(supplier_code: str, update_data: Dict[str, Any]):
    """Update an existing supplier profile."""
    updated = data_manager.update_supplier(supplier_code, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Supplier {supplier_code} not found.")
    return {"status": "SUCCESS", "message": f"Supplier {supplier_code} updated.", "supplier": updated}


@router.delete("/{supplier_code}", response_model=Dict[str, Any])
def delete_supplier(supplier_code: str):
    """Delete a supplier from the catalog."""
    deleted = data_manager.delete_supplier(supplier_code)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Supplier {supplier_code} not found.")
    return {"status": "SUCCESS", "message": f"Supplier {supplier_code} deleted successfully."}


@router.post("/reset-kaggle", response_model=Dict[str, Any])
def reset_to_kaggle_dataset():
    """Reset catalog to official Kaggle Supply Chain & DataCo benchmark distributions."""
    return data_manager.reset_to_kaggle_benchmarks()
