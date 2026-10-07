from backend.database.database import engine, Base, SessionLocal
from backend.database.models import (
    SupplierDB,
    CustomerOrderDB,
    FulfillmentTelemetryDB,
    CustomizationProfileDB,
    NegotiationSessionDB,
    NegotiationBidDB
)
from backend.services.data_manager import data_manager

def init_db():
    """Initializes tables and seeds database from dynamic/Kaggle datasets."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    try:
        # 1. Seed Suppliers if empty
        if session.query(SupplierDB).count() == 0:
            suppliers = data_manager.get_suppliers()
            for s in suppliers:
                session.add(
                    SupplierDB(
                        code=s["code"],
                        name=s["name"],
                        tier=s.get("tier", "Standard"),
                        country=s.get("country", "Global"),
                        unit_cost=float(s["unit_cost"]),
                        quality_score=float(s["quality_score"]),
                        on_time_delivery_rate=float(s["on_time_delivery_rate"]),
                        reliability_index=float(s["reliability_index"]),
                        risk_score=float(s["risk_score"]),
                        capacity_monthly=int(s.get("capacity_monthly", 50000)),
                        status=s.get("status", "ACTIVE")
                    )
                )
            session.commit()
            print(f"[Database] Seeded {len(suppliers)} suppliers.")

        # 2. Seed Customer Orders if empty
        if session.query(CustomerOrderDB).count() == 0:
            orders = data_manager.get_orders()
            for o in orders:
                session.add(
                    CustomerOrderDB(
                        order_id=o["order_id"],
                        customer_name=o["customer_name"],
                        customer_tier=o.get("customer_tier", "Standard Commercial"),
                        contact_email=o.get("contact_email", "procurement@client.com"),
                        sku_code=o.get("sku_code", "SKU-MC-772"),
                        quantity=int(o["quantity"]),
                        unit_price=float(o.get("unit_price", 145.0)),
                        order_value=float(o.get("order_value", 145000.0)),
                        promised_eta=o["promised_eta"],
                        revised_eta=o["revised_eta"],
                        delay_days=int(o.get("delay_days", 6)),
                        sla_penalty_exposure=float(o.get("sla_penalty_exposure", 0.0)),
                        status=o.get("status", "PENDING_ADVISORY")
                    )
                )
            session.commit()
            print(f"[Database] Seeded {len(orders)} customer orders.")

        # 3. Seed Fulfillment Telemetry if empty
        if session.query(FulfillmentTelemetryDB).count() == 0:
            telemetry = data_manager.get_fulfillment_history()
            for t in telemetry:
                session.add(
                    FulfillmentTelemetryDB(
                        record_id=t["record_id"],
                        unit_cost=float(t["unit_cost"]),
                        quality_score=float(t["quality_score"]),
                        on_time_delivery_rate=float(t["on_time_delivery_rate"]),
                        reliability_index=float(t["reliability_index"]),
                        risk_score=float(t["risk_score"]),
                        predicted_lead_time_days=float(t["predicted_lead_time_days"]),
                        actual_lead_time_days=float(t["actual_lead_time_days"]),
                        actual_optimal_decision=t["actual_optimal_decision"]
                    )
                )
            session.commit()
            print(f"[Database] Seeded {len(telemetry)} fulfillment telemetry records.")

        # 4. Seed Negotiation Session default if empty
        if session.query(NegotiationSessionDB).count() == 0:
            default_session = NegotiationSessionDB(
                session_id="SES-AUTONOMOUS-01",
                supplier_code="SUP-001",
                supplier_name="Apex Global Electronics",
                sku_code="SKU-MC-772",
                current_round=4,
                max_rounds=10,
                status="ACTIVE",
                buyer_target=142.50,
                supplier_target=165.00,
                current_offer=148.20,
                agreed_lead_time="12 Days",
                agent_confidence=94.8,
                estimated_savings=84200.0
            )
            session.add(default_session)
            session.commit()

            bids = [
                NegotiationBidDB(
                    session_id="SES-AUTONOMOUS-01",
                    round=1,
                    agent_id="SUPPLIER_AGENT",
                    agent_name="Apex Representative",
                    role="SUPPLIER",
                    proposed_price=165.00,
                    proposed_lead_time_days=18,
                    proposed_sla_confidence=88.0,
                    message="Initial batch quotation submitted for Micro-Capacitor SKU-MC-772 at $165.00/unit with 18-day lead time.",
                    status="COUNTERED"
                ),
                NegotiationBidDB(
                    session_id="SES-AUTONOMOUS-01",
                    round=2,
                    agent_id="BUYER_AGENT",
                    agent_name="Rimberio Buyer Lead",
                    role="BUYER",
                    proposed_price=142.50,
                    proposed_lead_time_days=10,
                    proposed_sla_confidence=95.0,
                    message="Counteroffer issued based on historical volume benchmark: Target $142.50/unit, 10 days delivery.",
                    status="COUNTERED"
                ),
                NegotiationBidDB(
                    session_id="SES-AUTONOMOUS-01",
                    round=3,
                    agent_id="LOGISTICS_AGENT",
                    agent_name="Maritime Telemetry Agent",
                    role="LOGISTICS",
                    proposed_price=145.00,
                    proposed_lead_time_days=14,
                    proposed_sla_confidence=91.5,
                    message="Suez congestion delta injects 4.2 days variance. Recommend locking 12-14 day buffered delivery corridor.",
                    status="ADVISORY"
                ),
                NegotiationBidDB(
                    session_id="SES-AUTONOMOUS-01",
                    round=4,
                    agent_id="BUYER_AGENT",
                    agent_name="Rimberio Buyer Lead",
                    role="BUYER",
                    proposed_price=148.20,
                    proposed_lead_time_days=12,
                    proposed_sla_confidence=94.8,
                    message="Autonomous compromise bid submitted at $148.20/unit with 12-day delivery guarantee.",
                    status="PENDING_RESPONSE"
                )
            ]
            session.add_all(bids)
            session.commit()
            print("[Database] Seeded default autonomous negotiation session and bids.")

    finally:
        session.close()

if __name__ == "__main__":
    init_db()
