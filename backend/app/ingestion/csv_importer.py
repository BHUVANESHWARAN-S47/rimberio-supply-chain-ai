import os
import uuid
import pandas as pd
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.database.models import (
    SupplierDB, ProductDB, CustomerDB, KaggleStagingDB, SupplierProductDB
)
from backend.app.ingestion.mappers import DataMapper

class CSVImporter:
    """Production-grade ingestion pipeline importing CSV datasets through staging into RIMBERIO relational tables."""

    def __init__(self, db: Session):
        self.db = db

    def import_dataset(
        self,
        file_path: str,
        entity_type: str,
        data_source: str = "PUBLIC_DATASET"
    ) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        df = pd.read_csv(file_path)
        batch_id = f"BATCH-{uuid.uuid4().hex[:8].upper()}"
        filename = os.path.basename(file_path)

        staged_count = 0
        inserted_count = 0
        skipped_count = 0
        errors = []

        # 1. Staging Phase
        staging_records = []
        for idx, row in df.iterrows():
            payload = row.to_dict()
            # Clean NaN values
            cleaned_payload = {k: (None if pd.isna(v) else v) for k, v in payload.items()}
            staging_records.append(
                KaggleStagingDB(
                    import_batch_id=batch_id,
                    dataset_name=filename,
                    row_index=int(idx),
                    raw_payload=cleaned_payload,
                    status="PENDING"
                )
            )
        self.db.add_all(staging_records)
        self.db.commit()
        staged_count = len(staging_records)

        # 2. Mapping & Production Resolution Phase
        for stage in staging_records:
            try:
                row = stage.raw_payload
                if entity_type == "supplier":
                    mapped = DataMapper.map_supplier_row(row, batch_id, data_source)
                    existing = self.db.query(SupplierDB).filter(SupplierDB.supplier_code == mapped["supplier_code"]).first()
                    if not existing:
                        supplier = SupplierDB(**mapped)
                        self.db.add(supplier)
                        inserted_count += 1
                        stage.status = "PROCESSED"
                    else:
                        skipped_count += 1
                        stage.status = "SKIPPED"

                elif entity_type == "product":
                    mapped = DataMapper.map_product_row(row, batch_id, data_source)
                    existing = self.db.query(ProductDB).filter(ProductDB.sku == mapped["sku"]).first()
                    if not existing:
                        product = ProductDB(**mapped)
                        self.db.add(product)
                        inserted_count += 1
                        stage.status = "PROCESSED"
                    else:
                        skipped_count += 1
                        stage.status = "SKIPPED"

                elif entity_type == "customer":
                    mapped = DataMapper.map_customer_row(row, batch_id, data_source)
                    existing = self.db.query(CustomerDB).filter(CustomerDB.customer_code == mapped["customer_code"]).first()
                    if not existing:
                        customer = CustomerDB(**mapped)
                        self.db.add(customer)
                        inserted_count += 1
                        stage.status = "PROCESSED"
                    else:
                        skipped_count += 1
                        stage.status = "SKIPPED"
                else:
                    stage.status = "SKIPPED"

            except Exception as e:
                stage.status = "ERROR"
                stage.error_log = str(e)
                errors.append({"row": stage.row_index, "error": str(e)})

        self.db.commit()

        return {
            "batch_id": batch_id,
            "filename": filename,
            "entity_type": entity_type,
            "staged_rows": staged_count,
            "inserted_rows": inserted_count,
            "skipped_duplicates": skipped_count,
            "error_count": len(errors),
            "errors": errors[:5]
        }
