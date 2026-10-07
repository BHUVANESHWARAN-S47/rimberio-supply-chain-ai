from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any, List
import pandas as pd
from backend.services.data_manager import data_manager, KAGGLE_DATACO_CSV, KAGGLE_SUPPLY_CHAIN_CSV

router = APIRouter(prefix="/api/data", tags=["Dynamic Dataset Ingestion & Kaggle Benchmarks"])

@router.get("/suppliers")
def get_raw_suppliers() -> List[Dict[str, Any]]:
    """Retrieve raw active suppliers dataset."""
    return data_manager.get_suppliers()

@router.post("/upload-suppliers-csv")
async def upload_suppliers_csv(file: UploadFile = File(...)):
    """
    Ingest ANY standard CSV supplier dataset.
    """
    try:
        content = (await file.read()).decode("utf-8")
        count = data_manager.import_suppliers_csv(content)
        return {
            "status": "SUCCESS",
            "imported_suppliers_count": count,
            "filename": file.filename,
            "message": f"Successfully ingested {count} supplier records from custom CSV."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

@router.post("/upload-kaggle-supplychain")
async def upload_kaggle_supplychain(file: UploadFile = File(...)):
    """
    Ingest official Kaggle 'Supply Chain Analysis' CSV (e.g. by Harshit Shankhdhar).
    Columns parsed: Supplier name, Location, Manufacturing costs, Defect rates, Lead times, Production volumes, Routes.
    Directly extracts vendor profiles and populates RIMBERIO's multi-criteria evaluation catalog.
    """
    try:
        content = (await file.read()).decode("utf-8")
        result = data_manager.import_kaggle_supply_chain_csv(content)
        if result.get("status") == "ERROR":
            raise HTTPException(status_code=400, detail=result.get("message"))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process Kaggle Supply Chain CSV: {str(e)}")

@router.post("/upload-kaggle-dataco")
async def upload_kaggle_dataco(file: UploadFile = File(...)):
    """
    Ingest official Kaggle 'DataCo Smart Supply Chain' CSV (DataCoSupplyChainDataset.csv).
    Columns parsed: Days for shipping (real), Days for shipment (scheduled), Late_delivery_risk, Customer Segment, Benefit per order, Sales.
    Directly powers the Continuous Learning Engine (MAE/RMSE) and Customer Impact SLA audits.
    """
    try:
        content = (await file.read()).decode("utf-8")
        result = data_manager.import_kaggle_dataco_csv(content)
        if result.get("status") == "ERROR":
            raise HTTPException(status_code=400, detail=result.get("message"))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process Kaggle DataCo CSV: {str(e)}")

@router.get("/kaggle/dataco-sample")
def get_kaggle_dataco_sample() -> List[Dict[str, Any]]:
    """Retrieve pre-loaded Kaggle DataCo sample records matching Kaggle's exact 53-column schema."""
    import os
    if os.path.exists(KAGGLE_DATACO_CSV):
        df = pd.read_csv(KAGGLE_DATACO_CSV)
        return df.to_dict(orient="records")
    return []

@router.get("/kaggle/supplychain-sample")
def get_kaggle_supplychain_sample() -> List[Dict[str, Any]]:
    """Retrieve pre-loaded Kaggle Supply Chain Analysis sample matching Kaggle's schema."""
    import os
    if os.path.exists(KAGGLE_SUPPLY_CHAIN_CSV):
        df = pd.read_csv(KAGGLE_SUPPLY_CHAIN_CSV)
        return df.to_dict(orient="records")
    return []

@router.get("/kaggle/summary")
def get_kaggle_summary() -> Dict[str, Any]:
    """Summary of active Kaggle datasets and mapped enterprise telemetry."""
    suppliers = data_manager.get_suppliers()
    orders = data_manager.get_orders()
    ful = data_manager.get_fulfillment_history()

    return {
        "status": "ONLINE",
        "supported_kaggle_benchmarks": [
            {
                "name": "DataCo Smart Supply Chain for Big Data Analysis",
                "kaggle_url": "https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis",
                "total_standard_columns": 53,
                "key_features_used": [
                    "Days for shipping (real)",
                    "Days for shipment (scheduled)",
                    "Late_delivery_risk",
                    "Benefit per order",
                    "Sales per customer",
                    "Customer Segment",
                    "Market",
                    "Delivery Status"
                ],
                "role_in_rimberio": "Powers continuous learning telemetry (MAE, RMSE), lead-time drift models, and customer SLA penalty audits."
            },
            {
                "name": "Supply Chain Analysis (Fashion & Beauty Startup)",
                "kaggle_url": "https://www.kaggle.com/datasets/harshitshankhdhar/supply-chain-analysis",
                "total_standard_columns": 24,
                "key_features_used": [
                    "Product type",
                    "SKU",
                    "Price",
                    "Supplier name",
                    "Location",
                    "Lead times",
                    "Production volumes",
                    "Manufacturing costs",
                    "Defect rates",
                    "Routes"
                ],
                "role_in_rimberio": "Powers autonomous supplier evaluation, defect-adjusted quality scores, margin utility curves, and adaptive switching MCDA."
            }
        ],
        "active_records_in_memory": {
            "total_suppliers": len(suppliers),
            "total_orders": len(orders),
            "total_fulfillment_records": len(ful)
        }
    }

@router.post("/generate-benchmark")
def generate_benchmark_dataset(suppliers_count: int = 50, orders_count: int = 100, fulfillment_records: int = 250):
    """Generate synthetic enterprise supply chain benchmark dataset of ANY size."""
    data_manager.generate_synthetic_suppliers(count=suppliers_count)
    data_manager.generate_synthetic_orders(count=orders_count)
    data_manager.generate_synthetic_fulfillment(count=fulfillment_records)
    data_manager.generate_kaggle_dataco_sample(count=50)
    data_manager.generate_kaggle_supply_chain_sample(count=50)

    return {
        "status": "SUCCESS",
        "suppliers_generated": suppliers_count,
        "orders_generated": orders_count,
        "fulfillment_records_generated": fulfillment_records,
        "message": f"Generated benchmark dataset conforming to Kaggle Supply Chain schemas."
    }
