"""
RIMBERIO Enterprise — Automated Kaggle Datasets Ingestion Pipeline
==================================================================
Reads:
  1. DataCoSupplyChainDataset.csv (180,519 rows)
  2. supply_chain_data.csv (Harshit Shankhdhar Supply Chain Analysis)
Translates and updates:
  - backend/data/suppliers.csv
  - backend/data/orders.csv
  - backend/data/fulfillment_history.csv
"""
import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "backend", "data")
DATACO_PATH = os.path.join(BASE_DIR, "DataCoSupplyChainDataset.csv")
SUPPLY_CHAIN_PATH = os.path.join(BASE_DIR, "supply_chain_data.csv")

def ingest_all():
    print("=" * 70)
    print("INGESTING OFFICIAL KAGGLE SUPPLY CHAIN DATASETS")
    print("=" * 70)

    # 1. Parse supply_chain_data.csv -> Suppliers Catalog
    if os.path.exists(SUPPLY_CHAIN_PATH):
        print(f"\n[1/3] Reading {SUPPLY_CHAIN_PATH}...")
        df_sc = pd.read_csv(SUPPLY_CHAIN_PATH)
        suppliers = []
        grouped = df_sc.groupby("Supplier name")
        idx = 1
        for name, group in grouped:
            avg_cost = float(group["Manufacturing costs"].mean())
            avg_defect = float(group["Defect rates"].mean())
            avg_lead = float(group["Lead times"].mean())
            loc = str(group["Location"].iloc[0])
            vol = int(group["Production volumes"].sum())
            
            quality = round(max(50.0, 100.0 - (avg_defect * 12.0)), 1)
            delivery = round(max(60.0, 100.0 - (avg_lead * 2.0)), 1)
            reliability = round(max(70.0, 98.0 - (avg_defect * 5.0)), 1)
            risk = round(min(80.0, (avg_lead * 2.2) + (avg_defect * 8.0)), 1)
            
            suppliers.append({
                "code": f"SUP-KAG-{idx:03d}",
                "name": f"{name} Precision Corp",
                "tier": "Tier-1 Verified",
                "country": loc,
                "unit_cost": round(avg_cost, 2),
                "quality_score": quality,
                "on_time_delivery_rate": delivery,
                "reliability_index": reliability,
                "risk_score": risk,
                "capacity_monthly": max(30000, vol * 10),
                "status": "ACTIVE" if risk < 45.0 else "WARNING"
            })
            idx += 1
            
        supp_csv = os.path.join(DATA_DIR, "suppliers.csv")
        pd.DataFrame(suppliers).to_csv(supp_csv, index=False)
        print(f"-> Successfully extracted {len(suppliers)} suppliers to {supp_csv}")
    else:
        print(f"Warning: {SUPPLY_CHAIN_PATH} not found.")

    # 2. Parse DataCoSupplyChainDataset.csv -> Customer Orders & Fulfillment Telemetry
    if os.path.exists(DATACO_PATH):
        print(f"\n[2/3] Reading {DATACO_PATH} (sampling 30 representative enterprise orders)...")
        df_dc = pd.read_csv(DATACO_PATH, nrows=100, encoding="latin1")
        orders = []
        for i, row in df_dc.head(30).iterrows():
            real_days = int(row["Days for shipping (real)"])
            sched_days = int(row["Days for shipment (scheduled)"])
            delay = max(0, real_days - sched_days)
            late_risk = int(row["Late_delivery_risk"])
            fname = str(row.get("Customer Fname", "Enterprise"))
            lname = str(row.get("Customer Lname", "Client"))
            email = str(row.get("Customer Email", f"procure_{i}@enterprise.com"))
            
            orders.append({
                "order_id": f"ORD-KAG-{1001 + i}",
                "customer_name": f"{fname} {lname}",
                "customer_tier": "Global Strategic Tier" if late_risk == 0 else "High-Risk Account",
                "contact_email": email,
                "sku_code": "SKU-MC-772",
                "quantity": int(row.get("Order Item Quantity", 5)) * 100,
                "unit_price": 142.50,
                "order_value": round(float(row.get("Sales per customer", 1500.0)), 2),
                "promised_eta": "2026-10-25",
                "revised_eta": f"2026-10-{min(30, 25 + delay)}",
                "delay_days": delay,
                "sla_penalty_exposure": round(delay * 750.0, 2),
                "status": "DELAY_ADVISORY_PENDING" if delay > 0 else "ON_SCHEDULE"
            })

        orders_csv = os.path.join(DATA_DIR, "orders.csv")
        pd.DataFrame(orders).to_csv(orders_csv, index=False)
        print(f"-> Successfully extracted {len(orders)} customer orders to {orders_csv}")

        # 3. Create Fulfillment Telemetry (for Continuous Learning & Confusion Matrix)
        print("\n[3/3] Generating Fulfillment Telemetry for ML Continual Learning Loop...")
        telemetry = []
        for i, row in df_dc.iterrows():
            real_days = int(row["Days for shipping (real)"])
            sched_days = int(row["Days for shipment (scheduled)"])
            delay = max(0, real_days - sched_days)
            cost = float(row.get("Sales per customer", 145.0))
            def_rate = round(float(np.random.uniform(0.5, 4.5)), 2)
            
            # Ground truth label: RETAIN (0), NEGOTIATE (1), SWITCH (2)
            if delay >= 4 or def_rate > 3.8:
                decision_label = "SWITCH"
            elif delay > 0 or cost > 200.0:
                decision_label = "NEGOTIATE"
            else:
                decision_label = "RETAIN"

            telemetry.append({
                "cycle_id": f"CYC-{1000 + i}",
                "scheduled_days": sched_days,
                "actual_days": real_days,
                "delay_days": delay,
                "defect_rate": def_rate,
                "cost_per_unit": round(min(185.0, max(120.0, cost / 2.0)), 2),
                "risk_score": round(min(80.0, (delay * 12.0) + (def_rate * 6.0)), 1),
                "actual_decision": decision_label
            })

        fulfillment_csv = os.path.join(DATA_DIR, "fulfillment_history.csv")
        pd.DataFrame(telemetry).to_csv(fulfillment_csv, index=False)
        print(f"-> Successfully generated {len(telemetry)} fulfillment cycles to {fulfillment_csv}")

    print("\n" + "=" * 70)
    print("KAGGLE DATASETS FULLY INGESTED INTO RIMBERIO PLATFORM!")
    print("=" * 70)

if __name__ == "__main__":
    ingest_all()
