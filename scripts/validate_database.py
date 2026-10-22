import os
import sys
from datetime import datetime

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import inspect, text, func
from backend.app.database.connection import SessionLocal, sync_engine, check_db_connection
from backend.app.database.models import (
    Base, SupplierDB, ProductDB, SupplierProductDB, CustomerDB, WarehouseDB,
    CarrierDB, PurchaseOrderDB, PurchaseOrderItemDB, ShipmentDB,
    SupplierPerformanceDB, QualityInspectionDB, CustomerOrderDB,
    NegotiationDB, NegotiationRoundDB, SimulationRunDB, SimulationScenarioDB,
    SimulationResultDB, AdaptiveDecisionDB, KaggleStagingDB
)
from backend.app.vector.client import check_chroma_connection

def validate_rimberio_database():
    print("=" * 60)
    print("      RIMBERIO ENTERPRISE DATABASE QUALITY CHECK")
    print("=" * 60)

    db = SessionLocal()
    inspector = inspect(sync_engine)
    report = {
        "passed": 0,
        "failed": 0,
        "checks": []
    }

    def record_check(name: str, passed: bool, details: str = ""):
        if passed:
            report["passed"] += 1
            print(f" [PASS] {name}: {details}")
        else:
            report["failed"] += 1
            print(f" [FAIL] {name}: {details}")
        report["checks"].append({"name": name, "passed": passed, "details": details})

    # 1. Database Connection
    db_conn = check_db_connection()
    record_check("Database Connection", db_conn["is_healthy"], f"Dialect: {db_conn.get('dialect')}")

    # 2. Migration Status
    try:
        ver = db.execute(text("SELECT version_num FROM alembic_version")).scalar()
        record_check("Alembic Migration Status", bool(ver), f"Current Revision: {ver}")
    except Exception as e:
        record_check("Alembic Migration Status", False, str(e))

    # 3. All Tables Exist
    existing_tables = set(inspector.get_table_names())
    expected_tables = set(Base.metadata.tables.keys())
    missing_tables = expected_tables - existing_tables
    record_check(
        "All Expected Tables Exist",
        len(missing_tables) == 0,
        f"Found {len(existing_tables)} tables (Missing: {len(missing_tables)})"
    )

    # 4. Check Foreign Keys
    fk_count = 0
    for tbl in expected_tables:
        fks = inspector.get_foreign_keys(tbl)
        fk_count += len(fks)
    record_check("Foreign Key Constraints Defined", fk_count > 20, f"Total Foreign Keys: {fk_count}")

    # 5. No Duplicate Business Identifiers
    dup_suppliers = db.query(SupplierDB.supplier_code).group_by(SupplierDB.supplier_code).having(func.count(SupplierDB.id) > 1).all()
    dup_skus = db.query(ProductDB.sku).group_by(ProductDB.sku).having(func.count(ProductDB.id) > 1).all()
    dup_customers = db.query(CustomerDB.customer_code).group_by(CustomerDB.customer_code).having(func.count(CustomerDB.id) > 1).all()
    record_check("Unique Supplier Codes", len(dup_suppliers) == 0, f"Duplicates: {len(dup_suppliers)}")
    record_check("Unique Product SKUs", len(dup_skus) == 0, f"Duplicates: {len(dup_skus)}")
    record_check("Unique Customer Codes", len(dup_customers) == 0, f"Duplicates: {len(dup_customers)}")

    # 6. No Invalid Negative Prices or Quantities
    neg_prices = db.query(ProductDB).filter(ProductDB.selling_price < 0).count()
    neg_costs = db.query(ProductDB).filter(ProductDB.unit_cost < 0).count()
    neg_po_qtys = db.query(PurchaseOrderItemDB).filter(PurchaseOrderItemDB.quantity_ordered <= 0).count()
    record_check("Non-Negative Product Prices", neg_prices == 0 and neg_costs == 0, "No negative prices or costs found")
    record_check("Positive Purchase Order Quantities", neg_po_qtys == 0, "All order line quantities > 0")

    # 7. No Impossible Dates (Chronological Consistency: order_date <= expected_delivery_date)
    date_violations = db.query(PurchaseOrderDB).filter(PurchaseOrderDB.expected_delivery_date < PurchaseOrderDB.order_date).count()
    record_check("Temporal Chronology Consistency", date_violations == 0, f"Chronological breaches: {date_violations}")

    # 8. No Orphan Records
    orphan_po_items = db.query(PurchaseOrderItemDB).filter(~PurchaseOrderItemDB.purchase_order_id.in_(db.query(PurchaseOrderDB.id))).count()
    orphan_neg_rounds = db.query(NegotiationRoundDB).filter(~NegotiationRoundDB.negotiation_id.in_(db.query(NegotiationDB.id))).count()
    record_check("Zero Orphan PO Items", orphan_po_items == 0, f"Orphans: {orphan_po_items}")
    record_check("Zero Orphan Negotiation Rounds", orphan_neg_rounds == 0, f"Orphans: {orphan_neg_rounds}")

    # 9. Seed Data Population Counts
    s_count = db.query(SupplierDB).count()
    p_count = db.query(ProductDB).count()
    sp_count = db.query(SupplierProductDB).count()
    po_count = db.query(PurchaseOrderDB).count()
    neg_count = db.query(NegotiationDB).count()
    sim_count = db.query(SimulationScenarioDB).count()
    record_check(
        "Relational Dataset Volume",
        s_count >= 50 and p_count >= 50 and po_count >= 100,
        f"{s_count} Suppliers, {p_count} Products, {sp_count} Links, {po_count} POs, {neg_count} Negotiations, {sim_count} Simulation Scenarios"
    )

    # 10. Data Provenance Verification
    non_provenance = db.query(SupplierDB).filter(SupplierDB.data_source.is_(None)).count()
    staged_kaggle = db.query(KaggleStagingDB).count()
    record_check("Data Provenance Tracking", non_provenance == 0 and staged_kaggle > 0, f"Staged Kaggle Records: {staged_kaggle}")

    # 11. ChromaDB Collections Health
    chroma_health = check_chroma_connection()
    record_check(
        "ChromaDB Vector Store Connected",
        chroma_health["is_healthy"] and chroma_health["collections_count"] == 6,
        f"{chroma_health['collections_count']}/6 Collections Available"
    )

    db.close()

    print("=" * 60)
    print(f"VERIFICATION SUMMARY: {report['passed']} PASSED, {report['failed']} FAILED")
    print(f"QUALITY GATE STATUS: {'PASS' if report['failed'] == 0 else 'FAIL'}")
    print("=" * 60)
    return report

if __name__ == "__main__":
    rep = validate_rimberio_database()
    if rep["failed"] > 0:
        sys.exit(1)
    sys.exit(0)
