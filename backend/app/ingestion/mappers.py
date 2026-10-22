import uuid
from typing import Dict, Any, Optional
from backend.app.ingestion.validators import DataIngestionValidator

v = DataIngestionValidator()

class DataMapper:
    """Translates arbitrary raw CSV/Excel rows into RIMBERIO relational entities."""

    @staticmethod
    def map_supplier_row(row: Dict[str, Any], batch_id: str, data_source: str = "IMPORTED_CSV") -> Dict[str, Any]:
        code = v.validate_string(row.get("code") or row.get("supplier_code") or row.get("Supplier ID") or f"SUP-{uuid.uuid4().hex[:6].upper()}")
        name = v.validate_string(row.get("name") or row.get("company_name") or row.get("Supplier name") or f"Supplier {code}")
        country = v.validate_string(row.get("country") or row.get("Country") or row.get("Location") or "Global")
        payment_terms = v.validate_string(row.get("payment_terms") or "Net 30")

        return {
            "supplier_code": code,
            "company_name": name,
            "contact_name": v.validate_string(row.get("contact_name") or f"{name} Procurement Desk"),
            "email": v.validate_string(row.get("email") or f"contact@{code.lower()}.com"),
            "phone": v.validate_string(row.get("phone") or "+1-800-555-0199"),
            "country": country,
            "city": v.validate_string(row.get("city") or row.get("City") or "Industrial Zone"),
            "status": "ACTIVE",
            "supplier_type": v.validate_string(row.get("tier") or row.get("supplier_type") or "STANDARD"),
            "payment_terms": payment_terms,
            "data_source": data_source,
            "source_reference": f"batch:{batch_id}"
        }

    @staticmethod
    def map_product_row(row: Dict[str, Any], batch_id: str, data_source: str = "PUBLIC_DATASET") -> Dict[str, Any]:
        sku = v.validate_string(row.get("SKU") or row.get("sku") or row.get("Product SKU") or f"SKU-{uuid.uuid4().hex[:6].upper()}")
        name = v.validate_string(row.get("name") or row.get("Product type") or row.get("Category Name") or f"Component {sku}")
        category = v.validate_string(row.get("Product type") or row.get("category") or row.get("Category Name") or "Industrial Parts")
        price = v.validate_positive_number(row.get("Price") or row.get("selling_price") or row.get("unit_price"), default=100.0)
        cost = v.validate_positive_number(row.get("unit_cost") or row.get("Cost"), default=price * 0.7)
        lead_time = v.validate_positive_int(row.get("Lead times") or row.get("lead_time_days") or row.get("Days for shipment (scheduled)"), default=12)

        return {
            "sku": sku,
            "name": name,
            "description": f"Standard enterprise component categorized under {category}.",
            "category": category,
            "unit": "unit",
            "unit_weight": v.validate_positive_number(row.get("unit_weight") or row.get("Weight"), default=1.5),
            "unit_cost": cost,
            "selling_price": price,
            "lead_time_days": lead_time,
            "safety_stock": 500,
            "reorder_point": 1000,
            "is_active": True,
            "data_source": data_source,
            "source_reference": f"batch:{batch_id}"
        }

    @staticmethod
    def map_customer_row(row: Dict[str, Any], batch_id: str, data_source: str = "IMPORTED_CSV") -> Dict[str, Any]:
        code = v.validate_string(row.get("customer_code") or row.get("Customer Id") or f"CUST-{uuid.uuid4().hex[:6].upper()}")
        name = v.validate_string(row.get("customer_name") or row.get("Customer Fname") or row.get("Name") or f"Enterprise Client {code}")
        country = v.validate_string(row.get("country") or row.get("Customer Country") or "United States")
        city = v.validate_string(row.get("city") or row.get("Customer City") or "Chicago")
        tier = v.validate_string(row.get("customer_tier") or row.get("Customer Segment") or "COMMERCIAL")
        priority = "CRITICAL" if "Tier 1" in tier or "Enterprise" in tier else "STANDARD"

        return {
            "customer_code": code,
            "name": name,
            "email": v.validate_string(row.get("contact_email") or row.get("Customer Email") or f"procurement@{code.lower()}.com"),
            "phone": "+1-800-444-0100",
            "country": country,
            "city": city,
            "customer_type": tier,
            "priority": priority,
            "data_source": data_source,
            "source_reference": f"batch:{batch_id}"
        }
