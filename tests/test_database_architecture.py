import os
import uuid
import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from backend.app.database.connection import SessionLocal
from backend.app.database.models import (
    Base, RoleDB, UserDB, SupplierDB, ProductDB, SupplierProductDB,
    CustomerDB, WarehouseDB, CarrierDB, RFQDB, RFQItemDB,
    QuotationDB, QuotationItemDB, PurchaseOrderDB, PurchaseOrderItemDB,
    NegotiationDB, NegotiationRoundDB, NegotiationMessageDB,
    SupplierPerformanceDB, InventoryDB, ShipmentDB, ShipmentEventDB,
    SimulationRunDB, SimulationScenarioDB, SimulationResultDB,
    AdaptiveDecisionDB, CustomerOrderDB, CustomerImpactDB,
    PredictionActualDB, ModelFeedbackDB, KaggleStagingDB
)
from backend.app.ingestion.csv_importer import CSVImporter
from backend.app.vector.client import get_chroma_client, check_chroma_connection
from backend.app.vector.collections import get_collection, COLLECTION_NAMES
from backend.app.vector.sync import ChromaSyncService
from backend.app.vector.embeddings import generate_embedding

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

# 1. Connection & Migration Tests
def test_01_database_connection(db):
    res = db.execute(Base.metadata.tables["roles"].select()).fetchall()
    assert len(res) > 0

def test_02_all_tables_registered_in_metadata():
    assert len(Base.metadata.tables) >= 48

# 2. RBAC & Master Data Tests
def test_03_rbac_roles_exist(db):
    role_names = [r.name for r in db.query(RoleDB).all()]
    for expected in ["ADMIN", "PROCUREMENT_MANAGER", "BUYER", "SUPPLIER", "CUSTOMER"]:
        assert expected in role_names

def test_04_user_role_assignment(db):
    user = db.query(UserDB).filter(UserDB.email == "buyer@rimberio.ai").first()
    assert user is not None
    assert user.role.name == "BUYER"

# 3. Unique Constraints & Identifiers
def test_05_supplier_code_uniqueness(db):
    existing = db.query(SupplierDB).first()
    dup = SupplierDB(
        supplier_code=existing.supplier_code,
        company_name="Duplicate Attempt Foundry",
        country="Global"
    )
    db.add(dup)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()

def test_06_product_sku_uniqueness(db):
    existing = db.query(ProductDB).first()
    dup = ProductDB(
        sku=existing.sku,
        name="Duplicate SKU Attempt",
        category="Test",
        unit_cost=50.0,
        selling_price=75.0
    )
    db.add(dup)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()

def test_07_customer_code_uniqueness(db):
    existing = db.query(CustomerDB).first()
    dup = CustomerDB(
        customer_code=existing.customer_code,
        name="Duplicate Customer Attempt"
    )
    db.add(dup)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()

# 4. Supplier-Product Relationship
def test_08_supplier_product_relationship(db):
    sp = db.query(SupplierProductDB).first()
    assert sp is not None
    assert sp.supplier is not None
    assert sp.product is not None
    assert sp.unit_price > 0

def test_09_supplier_product_unique_combination(db):
    sp = db.query(SupplierProductDB).first()
    dup = SupplierProductDB(
        supplier_id=sp.supplier_id,
        product_id=sp.product_id,
        unit_price=sp.unit_price
    )
    db.add(dup)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()

# 5. Purchase Order & Temporal Consistency
def test_10_purchase_order_relationships(db):
    po = db.query(PurchaseOrderDB).first()
    assert po is not None
    assert po.supplier is not None
    assert po.buyer is not None
    assert len(po.items) > 0
    assert po.items[0].quantity_ordered > 0

def test_11_temporal_consistency(db):
    pos = db.query(PurchaseOrderDB).all()
    for po in pos:
        assert po.order_date <= po.expected_delivery_date

# 6. Negotiation Domain
def test_12_negotiation_multi_round_integrity(db):
    neg = db.query(NegotiationDB).filter(NegotiationDB.current_round >= 2).first()
    assert neg is not None
    rounds = db.query(NegotiationRoundDB).filter(NegotiationRoundDB.negotiation_id == neg.id).all()
    assert len(rounds) >= 2
    for r in rounds:
        assert r.offered_price > 0
        assert r.quantity > 0

# 7. Logistics & Shipments
def test_13_shipment_carrier_link(db):
    shp = db.query(ShipmentDB).first()
    assert shp is not None
    assert shp.carrier is not None
    assert shp.shipping_cost >= 0
    assert shp.distance >= 0

# 8. Counterfactual Simulation (CNT) Domain
def test_14_cnt_simulation_hierarchy(db):
    run = db.query(SimulationRunDB).filter(SimulationRunDB.run_id == "CNT-EXP-PAPER-BASELINE").first()
    assert run is not None
    assert len(run.scenarios) == 8
    sc_types = [s.scenario_type for s in run.scenarios]
    assert "NORMAL" in sc_types
    assert "SUPPLIER_DELAY" in sc_types
    assert "TRANSPORT_DISRUPTION" in sc_types

    first_scenario = run.scenarios[0]
    assert len(first_scenario.results) > 0
    res = first_scenario.results[0]
    assert res.candidate_price > 0
    assert res.predicted_cost > 0
    assert 0.0 <= res.predicted_stockout_rate <= 1.0

def test_15_adaptive_decision_relationship(db):
    run = db.query(SimulationRunDB).filter(SimulationRunDB.run_id == "CNT-EXP-PAPER-BASELINE").first()
    assert run.decision is not None
    assert run.decision.decision_type in ["RETAIN", "NEGOTIATE", "SWITCH"]
    assert run.decision.confidence > 0.8

# 9. Customer Order & Impact Tracking
def test_16_customer_orders_linkage(db):
    order = db.query(CustomerOrderDB).first()
    assert order is not None
    assert order.customer is not None
    assert order.product is not None
    assert order.quantity > 0

# 10. Data Ingestion & Staging
def test_17_kaggle_staging_provenance(db):
    staged = db.query(KaggleStagingDB).all()
    assert len(staged) > 0
    assert staged[0].import_batch_id.startswith("BATCH-")
    assert staged[0].status in ["PROCESSED", "SKIPPED"]

def test_18_duplicate_import_idempotency(db):
    importer = CSVImporter(db)
    suppliers_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "data", "suppliers.csv"))
    if os.path.exists(suppliers_csv):
        # Ensure base dataset is imported first
        importer.import_dataset(suppliers_csv, entity_type="supplier")
        # Attempt duplicate import — must be idempotent
        res = importer.import_dataset(suppliers_csv, entity_type="supplier")
        assert res["inserted_rows"] == 0
        assert res["skipped_duplicates"] > 0

# 11. ChromaDB Vector Integration
def test_19_chroma_collections_registered():
    client = get_chroma_client()
    cols = client.list_collections()
    col_names = [c.name for c in cols]
    for req in COLLECTION_NAMES:
        assert req in col_names

def test_20_chroma_health_probe():
    health = check_chroma_connection()
    assert health["is_healthy"] is True
    assert health["collections_count"] == 6

def test_21_chroma_semantic_retrieval():
    client = get_chroma_client()
    for name in [
        "rimberio_supplier_memory",
        "rimberio_negotiation_memory",
        "rimberio_decision_memory",
        "rimberio_simulation_memory"
    ]:
        col = client.get_collection(name)
        assert col.name == name
        assert "description" in col.metadata

# 12. Feedback Loop Architecture
def test_22_feedback_loop_records(db):
    res = db.query(SimulationResultDB).first()
    pred_act = PredictionActualDB(
        simulation_result_id=res.id,
        actual_supplier_id=res.candidate_supplier_id,
        actual_cost=res.predicted_cost * 1.02,
        actual_delivery_days=res.candidate_delivery_days + 1,
        actual_inventory=res.predicted_inventory - 50,
        actual_stockout_rate=0.01,
        actual_service_level=96.0,
        actual_customer_impact=0.0
    )
    db.add(pred_act)
    db.flush()

    fb = ModelFeedbackDB(
        prediction_actual_id=pred_act.id,
        metric_name="cost",
        predicted_value=res.predicted_cost,
        actual_value=pred_act.actual_cost,
        error=res.predicted_cost - pred_act.actual_cost,
        absolute_error=abs(res.predicted_cost - pred_act.actual_cost),
        percentage_error=abs(res.predicted_cost - pred_act.actual_cost) / pred_act.actual_cost * 100.0,
        model_version="CNT_SIMULATOR_V2"
    )
    db.add(fb)
    db.commit()

    retrieved_fb = db.query(ModelFeedbackDB).filter(ModelFeedbackDB.id == fb.id).first()
    assert retrieved_fb is not None
    assert retrieved_fb.percentage_error < 5.0
