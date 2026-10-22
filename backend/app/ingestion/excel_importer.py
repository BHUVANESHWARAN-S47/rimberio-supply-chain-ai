import os
import uuid
import pandas as pd
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.app.ingestion.csv_importer import CSVImporter

class ExcelImporter:
    """Imports Excel spreadsheets (.xlsx, .xls) by converting worksheets and routing through the staged pipeline."""

    def __init__(self, db: Session):
        self.db = db
        self.csv_importer = CSVImporter(db)

    def import_excel_sheet(
        self,
        file_path: str,
        entity_type: str,
        sheet_name: str = 0,
        data_source: str = "IMPORTED_EXCEL"
    ) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        df = pd.read_excel(file_path, sheet_name=sheet_name)
        temp_csv = f"{file_path}.temp.csv"
        try:
            df.to_csv(temp_csv, index=False)
            result = self.csv_importer.import_dataset(
                temp_csv,
                entity_type=entity_type,
                data_source=data_source
            )
            result["source_format"] = "EXCEL"
            return result
        finally:
            if os.path.exists(temp_csv):
                os.remove(temp_csv)
