import os
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.database.connection import SessionLocal
from backend.app.database.models import (
    RoleDB, UserDB, SupplierDB, ProductDB, SupplierProductDB,
    CustomerDB, WarehouseDB, CarrierDB, RFQDB, RFQItemDB,
    QuotationDB, QuotationItemDB, PurchaseOrderDB, PurchaseOrderItemDB,
    NegotiationDB, NegotiationRoundDB, NegotiationMessageDB,
    SupplierPerformanceDB, InventoryDB, DemandHistoryDB, DemandForecastDB,
    ShipmentDB, ShipmentEventDB, QualityInspectionDB, RiskEventDB, RiskAssessmentDB,
    SimulationRunDB, SimulationScenarioDB, SimulationResultDB,
    SupplierComparisonDB, AdaptiveDecisionDB, CustomerOrderDB, CustomerOrderItemDB,
    CustomerImpactDB, CustomerNotificationDB
)
from backend.app.ingestion.csv_importer import CSVImporter

def generate_enterprise_seed(
    num_suppliers: int = 50,
    num_products: int = 100,
    num_customers: int = 100,
    num_pos: int = 250,
    num_rfqs: int = 50,
    num_negotiations: int = 50,
    is_demo: bool = True
):
    """Generates a fully interconnected, chronologically consistent relational supply chain dataset."""
    db: Session = SessionLocal()
    print(">>> Starting RIMBERIO Relational Database Seeding...")

    try:
        # 1. Roles & Default Users
        roles = {
            "ADMIN": "System Administrator with full access",
            "PROCUREMENT_MANAGER": "Manager supervising procurement operations",
            "BUYER": "Enterprise buyer issuing RFQs and negotiating proposals",
            "SUPPLY_CHAIN_ANALYST": "Analyst monitoring risks and simulations",
            "LOGISTICS_MANAGER": "Manager tracking carriers and transit routes",
            "SUPPLIER": "Supplier representative submitting quotations",
            "CUSTOMER": "Client purchasing finished goods"
        }
        role_objs = {}
        for r_name, r_desc in roles.items():
            r = db.query(RoleDB).filter(RoleDB.name == r_name).first()
            if not r:
                r = RoleDB(name=r_name, description=r_desc)
                db.add(r)
                db.flush()
            role_objs[r_name] = r

        # Default Buyer User
        buyer_user = db.query(UserDB).filter(UserDB.email == "buyer@rimberio.ai").first()
        if not buyer_user:
            buyer_user = UserDB(
                email="buyer@rimberio.ai",
                password_hash="scrypt_hash_simulated_buyer",
                full_name="Sarah Jenkins (Senior Procurement Lead)",
                role_id=role_objs["BUYER"].id
            )
            db.add(buyer_user)
            db.flush()

        # 2. Ingest Kaggle Sample Data First
        importer = CSVImporter(db)
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))

        suppliers_csv = os.path.join(data_dir, "suppliers.csv")
        if os.path.exists(suppliers_csv):
            print(" - Ingesting Kaggle suppliers...")
            importer.import_dataset(suppliers_csv, entity_type="supplier", data_source="PUBLIC_DATASET")

        products_csv = os.path.join(data_dir, "kaggle_supply_chain_analysis_sample.csv")
        if os.path.exists(products_csv):
            print(" - Ingesting Kaggle supply chain products...")
            importer.import_dataset(products_csv, entity_type="product", data_source="PUBLIC_DATASET")

        orders_csv = os.path.join(data_dir, "orders.csv")
        if os.path.exists(orders_csv):
            print(" - Ingesting customer orders reference...")
            importer.import_dataset(orders_csv, entity_type="customer", data_source="PUBLIC_DATASET")

        # 3. Warehouses & Carriers
        warehouses = []
        for i in range(1, 11):
            w_code = f"WH-{i:03d}"
            w = db.query(WarehouseDB).filter(WarehouseDB.warehouse_code == w_code).first()
            if not w:
                w = WarehouseDB(
                    warehouse_code=w_code,
                    name=f"Rimberio Fulfillment Hub {i}",
                    city=["Rotterdam", "Singapore", "Hamburg", "Long Beach", "Dubai", "Shanghai", "Mumbai", "Antwerp", "Busan", "Chicago"][i-1],
                    country=["Netherlands", "Singapore", "Germany", "United States", "UAE", "China", "India", "Belgium", "South Korea", "United States"][i-1],
                    capacity=150000 + i * 10000
                )
                db.add(w)
                db.flush()
            warehouses.append(w)

        carriers = []
        carrier_names = [
            ("CAR-01", "Maersk Ocean Line", "MARITIME", 18.0, 94.5),
            ("CAR-02", "DHL Global Forwarding", "AIR_EXPRESS", 3.0, 98.2),
            ("CAR-03", "Kuehne + Nagel Rail", "INTERMODAL", 12.0, 92.0),
            ("CAR-04", "Mediterranean Shipping Co", "MARITIME", 20.0, 89.5),
            ("CAR-05", "FedEx Freight Cargo", "TRUCKING", 4.0, 96.0)
        ]
        for c_code, c_name, s_type, transit, rel in carrier_names:
            c = db.query(CarrierDB).filter(CarrierDB.carrier_code == c_code).first()
            if not c:
                c = CarrierDB(
                    carrier_code=c_code,
                    name=c_name,
                    service_type=s_type,
                    average_transit_days=transit,
                    reliability_score=rel
                )
                db.add(c)
                db.flush()
            carriers.append(c)

        # 4. Synthesize Remaining Suppliers & Products up to target
        existing_suppliers = db.query(SupplierDB).all()
        for idx in range(len(existing_suppliers), num_suppliers):
            code = f"SUP-SYN-{idx+1:04d}"
            supp = SupplierDB(
                supplier_code=code,
                company_name=f"Global Precision Foundry {idx+1}",
                contact_name=f"Representative {idx+1}",
                email=f"sales@{code.lower()}.com",
                country=["United States", "Germany", "Taiwan", "Japan", "South Korea", "Vietnam"][idx % 6],
                city="High-Tech Cluster",
                status="ACTIVE",
                supplier_type="TIER_1" if idx % 3 == 0 else "STANDARD",
                payment_terms=["Net 30", "Net 45", "Net 60"][idx % 3],
                data_source="SYNTHETIC",
                source_reference="enterprise_seed_v1"
            )
            db.add(supp)
            db.flush()
            existing_suppliers.append(supp)

        existing_products = db.query(ProductDB).all()
        for idx in range(len(existing_products), num_products):
            sku = f"SKU-SYN-{idx+1:04d}"
            cost = round(random.uniform(25.0, 280.0), 2)
            prod = ProductDB(
                sku=sku,
                name=f"Microcontroller Core Series {idx+1}",
                category="Semiconductors" if idx % 2 == 0 else "Electronic Assemblies",
                unit="unit",
                unit_weight=round(random.uniform(0.1, 4.5), 2),
                unit_cost=cost,
                selling_price=round(cost * 1.35, 2),
                lead_time_days=random.randint(7, 30),
                safety_stock=random.randint(200, 1000),
                reorder_point=random.randint(1000, 2500),
                data_source="SYNTHETIC",
                source_reference="enterprise_seed_v1"
            )
            db.add(prod)
            db.flush()
            existing_products.append(prod)

        # 5. Connect Supplier-Product Relationships
        print(" - Connecting Supplier-Product relationships...")
        for supp in existing_suppliers[:num_suppliers]:
            sample_prods = random.sample(existing_products, min(len(existing_products), 5))
            for p in sample_prods:
                sp = db.query(SupplierProductDB).filter(
                    SupplierProductDB.supplier_id == supp.id,
                    SupplierProductDB.product_id == p.id
                ).first()
                if not sp:
                    sp = SupplierProductDB(
                        supplier_id=supp.id,
                        product_id=p.id,
                        supplier_sku=f"S-{p.sku}",
                        unit_price=round(p.unit_cost * random.uniform(0.95, 1.15), 2),
                        minimum_order_quantity=random.choice([100, 250, 500, 1000]),
                        lead_time_days=p.lead_time_days + random.randint(-3, 5),
                        capacity=random.randint(10000, 100000),
                        quality_rating=round(random.uniform(88.0, 98.5), 1)
                    )
                    db.add(sp)
        db.commit()

        # 6. Customers
        existing_customers = db.query(CustomerDB).all()
        for idx in range(len(existing_customers), num_customers):
            c_code = f"CUST-SYN-{idx+1:04d}"
            cust = CustomerDB(
                customer_code=c_code,
                name=f"Enterprise Tier Client {idx+1}",
                email=f"procurement@{c_code.lower()}.com",
                customer_type="ENTERPRISE_OEM" if idx % 3 == 0 else "COMMERCIAL",
                priority="CRITICAL" if idx % 4 == 0 else "STANDARD",
                data_source="SYNTHETIC",
                source_reference="enterprise_seed_v1"
            )
            db.add(cust)
            db.flush()
            existing_customers.append(cust)

        # 7. Relational Transactions: RFQ -> Quotation -> Negotiation -> PO -> Shipment -> Performance
        print(f" - Generating {num_pos} interconnected transactional procurement episodes...")
        base_time = datetime.utcnow() - timedelta(days=180)

        for i in range(num_pos):
            supp = random.choice(existing_suppliers)
            prod = random.choice(existing_products)
            cust = random.choice(existing_customers)
            wh = random.choice(warehouses)
            carrier = random.choice(carriers)

            # Chronology:
            t_rfq = base_time + timedelta(days=i * 0.6)
            t_quote = t_rfq + timedelta(days=2)
            t_neg = t_quote + timedelta(days=2)
            t_po = t_neg + timedelta(days=2)
            t_ship = t_po + timedelta(days=prod.lead_time_days)
            t_arrival = t_ship + timedelta(days=int(carrier.average_transit_days))

            qty = random.choice([500, 1000, 2000, 5000])
            unit_price = round(prod.unit_cost * random.uniform(0.98, 1.08), 2)
            total_amount = round(qty * unit_price, 2)

            # Purchase Order
            po = PurchaseOrderDB(
                po_number=f"PO-{20260000 + i}",
                supplier_id=supp.id,
                buyer_id=buyer_user.id,
                status="DELIVERED",
                order_date=t_po,
                expected_delivery_date=t_arrival,
                actual_delivery_date=t_arrival + timedelta(days=random.choice([0, 0, 0, 1, 3, -1])),
                total_amount=total_amount,
                currency="USD"
            )
            db.add(po)
            db.flush()

            # PO Line Item
            defects = random.randint(0, int(qty * 0.02))
            po_item = PurchaseOrderItemDB(
                purchase_order_id=po.id,
                product_id=prod.id,
                quantity_ordered=qty,
                quantity_received=qty,
                unit_price=unit_price,
                defective_quantity=defects
            )
            db.add(po_item)

            # Shipment
            shipment = ShipmentDB(
                shipment_number=f"SHP-{20260000 + i}",
                purchase_order_id=po.id,
                supplier_id=supp.id,
                carrier_id=carrier.id,
                origin=f"{supp.country} Facility",
                destination=f"{wh.name}",
                planned_departure=t_ship,
                actual_departure=t_ship,
                planned_arrival=t_arrival,
                actual_arrival=po.actual_delivery_date,
                status="DELIVERED",
                shipping_cost=round(random.uniform(1200.0, 8500.0), 2),
                distance=random.uniform(500.0, 9500.0),
                created_at=t_ship
            )
            db.add(shipment)

            # Performance record
            is_ontime = (po.actual_delivery_date <= po.expected_delivery_date)
            quality_score = round(max(80.0, 100.0 - (defects / qty * 1000.0)), 1)
            perf = SupplierPerformanceDB(
                supplier_id=supp.id,
                purchase_order_id=po.id,
                product_id=prod.id,
                promised_delivery_date=po.expected_delivery_date,
                actual_delivery_date=po.actual_delivery_date,
                ordered_quantity=qty,
                received_quantity=qty,
                defective_quantity=defects,
                unit_price=unit_price,
                lead_time_days=(po.actual_delivery_date - po.order_date).days,
                on_time=is_ontime,
                quality_score=quality_score,
                recorded_at=po.actual_delivery_date
            )
            db.add(perf)

            # Quality Inspection
            insp = QualityInspectionDB(
                supplier_id=supp.id,
                product_id=prod.id,
                purchase_order_id=po.id,
                inspection_date=po.actual_delivery_date,
                quantity_inspected=qty,
                quantity_passed=qty - defects,
                quantity_failed=defects,
                quality_score=quality_score,
                defect_rate=round(defects / qty * 100.0, 2),
                notes="Standard QA lot sampling passed" if defects < 10 else "Minor cosmetic deviation within tolerance"
            )
            db.add(insp)

            # Customer Order linked
            cust_order = CustomerOrderDB(
                order_number=f"ORD-CUST-{20260000 + i}",
                customer_id=cust.id,
                product_id=prod.id,
                quantity=int(qty * 0.8),
                unit_price=prod.selling_price,
                total_amount=round(qty * 0.8 * prod.selling_price, 2),
                order_date=t_po - timedelta(days=5),
                promised_delivery_date=t_arrival + timedelta(days=4),
                status="IN_FULFILLMENT" if i > (num_pos - 15) else "DELIVERED"
            )
            db.add(cust_order)

        # 8. Negotiations & Rounds
        print(f" - Generating {num_negotiations} multi-round negotiation episodes...")
        for j in range(num_negotiations):
            supp = random.choice(existing_suppliers)
            prod = random.choice(existing_products)
            neg = NegotiationDB(
                supplier_id=supp.id,
                buyer_id=buyer_user.id,
                status="AGREED" if j % 3 != 0 else "IN_PROGRESS",
                current_round=3,
                started_at=datetime.utcnow() - timedelta(days=random.randint(5, 30))
            )
            db.add(neg)
            db.flush()

            base_price = prod.unit_cost
            rounds_data = [
                (1, "BUYER", buyer_user.email, base_price * 0.90, "Initial target offer"),
                (2, "SUPPLIER", supp.supplier_code, base_price * 1.05, "Counteroffer taking margin into account"),
                (3, "BUYER", buyer_user.email, base_price * 0.98, "Compromise price with Net 45 terms")
            ]
            for r_num, actor_type, actor_id, price, note in rounds_data:
                round_rec = NegotiationRoundDB(
                    negotiation_id=neg.id,
                    round_number=r_num,
                    actor_type=actor_type,
                    actor_id=actor_id,
                    offered_price=round(price, 2),
                    quantity=1000,
                    delivery_days=prod.lead_time_days,
                    quality_level=95.0,
                    payment_terms="Net 45",
                    proposal=note,
                    accepted=(r_num == 3 and neg.status == "AGREED"),
                    timestamp=neg.started_at + timedelta(hours=r_num * 12)
                )
                db.add(round_rec)

        # 9. Research Experiment Simulation Data (Section 39)
        print(" - Generating Counterfactual Simulation (CNT) research baseline scenarios...")
        sim_run = SimulationRunDB(
            run_id="CNT-EXP-PAPER-BASELINE",
            trigger_type="DISRUPTION_ALERT",
            baseline_reference="Incumbent Supplier vs 3 Counterfactual Candidates",
            status="COMPLETED"
        )
        db.add(sim_run)
        db.flush()

        scenarios = [
            ("NORMAL", "Baseline operations with steady market demand"),
            ("HIGH_DEMAND", "Surge in procurement orders +35%"),
            ("LOW_DEMAND", "Contraction in demand -20%"),
            ("SUPPLIER_DELAY", "Primary supplier factory maintenance delay +14 days"),
            ("TRANSPORT_DISRUPTION", "Suez maritime canal bottleneck +21 days transit"),
            ("SUPPLY_SHORTAGE", "Silicon raw material shortage cutting supplier allocation by 40%"),
            ("PRICE_INCREASE", "Raw material inflation increasing unit price by 15%"),
            ("INVENTORY_SHORTAGE", "Safety stock drawdown below reorder threshold")
        ]
        for sc_type, sc_desc in scenarios:
            sc = SimulationScenarioDB(
                simulation_run_id=sim_run.id,
                scenario_type=sc_type,
                description=sc_desc,
                assumptions={"surge_multiplier": 1.35 if sc_type == "HIGH_DEMAND" else 1.0}
            )
            db.add(sc)
            db.flush()

            for cand_supp in existing_suppliers[:3]:
                res = SimulationResultDB(
                    simulation_scenario_id=sc.id,
                    candidate_supplier_id=cand_supp.id,
                    candidate_price=145.0,
                    candidate_delivery_days=12,
                    predicted_cost=145000.0,
                    predicted_profit=42500.0,
                    predicted_inventory=1200,
                    predicted_delivery_delay=2.5 if sc_type == "SUPPLIER_DELAY" else 0.5,
                    predicted_stockout_rate=0.08 if sc_type == "SUPPLY_SHORTAGE" else 0.01,
                    predicted_risk=22.5,
                    predicted_service_level=96.4,
                    predicted_customer_impact=0.0,
                    prediction_confidence=0.94
                )
                db.add(res)

        # Adaptive Decision
        decision = AdaptiveDecisionDB(
            simulation_run_id=sim_run.id,
            selected_supplier_id=existing_suppliers[1].id,
            decision_type="SWITCH",
            confidence=0.96,
            reasoning="Switching to alternate candidate protects margin from Suez maritime delay with 12-day local lead time.",
            decision_factors={"risk_delta": -18.2, "cost_saving": 210000.0}
        )
        db.add(decision)

        db.commit()
        print(">>> Relational Database Seeding Successfully Completed!")
        return {"status": "SUCCESS", "suppliers": len(existing_suppliers), "products": len(existing_products)}

    except Exception as e:
        db.rollback()
        print(f"!!! Error during database seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    generate_enterprise_seed()
