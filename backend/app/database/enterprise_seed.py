import uuid
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.app.database.connection import SessionLocal, sync_engine
from backend.app.database.models import (
    Base, OrganizationDB, DepartmentDB, PermissionDB, RoleDB, RolePermissionDB,
    UserDB, UserRoleDB, AIAgentDB, AICapabilityDB, RoleAICapabilityDB,
    SupplierDB, ProductDB, CustomerDB, WarehouseDB, CarrierDB
)
from backend.app.core.security import get_password_hash

def seed_enterprise_hierarchy():
    """Seed comprehensive multi-tenant organization, department, RBAC, and AI capability structure."""
    Base.metadata.create_all(bind=sync_engine)
    db: Session = SessionLocal()

    try:
        # ── 1. Create Default Multi-Industry Organizations ──
        org_data = [
            {
                "id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
                "name": "Rimberio Global Dynamics",
                "industry": "Electronics & High-Tech",
                "country": "United States",
                "location": "San Jose, CA",
                "contact_email": "enterprise@rimberio.ai",
                "contact_phone": "+1-408-555-0199",
                "settings_json": '{"currency": "USD", "sla_threshold_days": 2, "quality_standard": "Mil-Spec 883"}',
            },
            {
                "id": uuid.UUID("22222222-2222-2222-2222-222222222222"),
                "name": "Apex Horizon Textiles Ltd",
                "industry": "Textile & Apparel",
                "country": "India",
                "location": "Tirupur, Tamil Nadu",
                "contact_email": "ops@apextextiles.in",
                "contact_phone": "+91-421-555-0188",
                "settings_json": '{"currency": "INR", "sla_threshold_days": 3, "quality_metric": "GSM"}',
            },
            {
                "id": uuid.UUID("33333333-3333-3333-3333-333333333333"),
                "name": "Verdant Pure Dairy Co.",
                "industry": "Dairy & Food Processing",
                "country": "New Zealand",
                "location": "Waikato",
                "contact_email": "procure@verdantdairy.nz",
                "contact_phone": "+64-7-555-0177",
                "settings_json": '{"currency": "NZD", "sla_threshold_days": 1, "quality_metric": "Fat Content %"}',
            },
            {
                "id": uuid.UUID("44444444-4444-4444-4444-444444444444"),
                "name": "Nordic Precision Automotive AG",
                "industry": "Automotive & Industrial",
                "country": "Germany",
                "location": "Stuttgart",
                "contact_email": "supply@nordicauto.de",
                "contact_phone": "+49-711-555-0166",
                "settings_json": '{"currency": "EUR", "sla_threshold_days": 2, "quality_standard": "ISO/TS 16949"}',
            },
        ]

        org_objs = {}
        for d in org_data:
            org = db.query(OrganizationDB).filter(OrganizationDB.id == d["id"]).first()
            if not org:
                org = OrganizationDB(**d)
                db.add(org)
                db.flush()
            org_objs[d["name"]] = org

        primary_org = org_objs["Rimberio Global Dynamics"]

        # ── 2. Create Departments for Primary Organization ──
        dept_data = [
            {"code": "PROC", "name": "Procurement", "desc": "Sourcing, RFQs, vendor bargaining, and purchasing."},
            {"code": "SCM", "name": "Supply Chain & Risk", "desc": "Demand forecasting, twin simulations, and risk assessment."},
            {"code": "LOG", "name": "Logistics & Freight", "desc": "Carrier management, live vessel tracking, and port routing."},
            {"code": "QA", "name": "Quality Assurance", "desc": "Defect tracking, supplier auditing, and certification compliance."},
            {"code": "FIN", "name": "Finance & Spend", "desc": "Procurement budget audits, payment terms, and spend analytics."},
            {"code": "OPS", "name": "Customer Operations", "desc": "Order fulfillment, client notices, and downstream SLA monitoring."},
            {"code": "ADMIN", "name": "Administration & IT", "desc": "Tenant governance, user roles, security, and audit logs."},
        ]

        dept_objs = {}
        for d in dept_data:
            dept = db.query(DepartmentDB).filter(
                DepartmentDB.organization_id == primary_org.id,
                DepartmentDB.code == d["code"]
            ).first()
            if not dept:
                dept = DepartmentDB(
                    organization_id=primary_org.id,
                    name=d["name"],
                    code=d["code"],
                    description=d["desc"],
                )
                db.add(dept)
                db.flush()
            dept_objs[d["code"]] = dept

        # ── 3. Create Standard System Roles ──
        role_definitions = [
            ("ADMIN", "System Administrator", "Platform governance, tenant management, and user provisioning."),
            ("PROCUREMENT_MANAGER", "Procurement Manager", "Oversees purchasing, evaluates vendor switches, approves POs."),
            ("BUYER", "Enterprise Buyer", "Finds suppliers, drafts RFQs, negotiates terms, and issues draft POs."),
            ("SUPPLY_CHAIN_ANALYST", "Supply Chain Analyst", "Monitors inventory, models macro disruptions, runs CNT simulations."),
            ("LOGISTICS_MANAGER", "Logistics Manager", "Manages multimodal freight carriers and mitigates shipping bottlenecks."),
            ("QUALITY_CONTROLLER", "Quality Controller", "Inspects inbound lots, records defect PPMs, verifies QA certificates."),
            ("FINANCE_ANALYST", "Finance Analyst", "Audits procurement cash flow, verifies budgets, and tracks savings."),
            ("SUPPLIER", "External Supplier Partner", "External vendor: submits quotes, accepts negotiations and POs."),
            ("CUSTOMER", "External Enterprise Client", "External buyer: tracks orders, shipments, and delivery milestones."),
        ]

        role_objs = {}
        for name, d_name, desc in role_definitions:
            r = db.query(RoleDB).filter(RoleDB.name == name).first()
            if not r:
                r = RoleDB(name=name, display_name=d_name, description=desc, is_system=True)
                db.add(r)
                db.flush()
            role_objs[name] = r

        # ── 4. Create Granular Platform Permissions ──
        permissions_data = [
            # Supplier & Sourcing
            ("supplier.read", "View Suppliers", "PROCUREMENT", "Access supplier catalogs and profiles."),
            ("supplier.create", "Create Supplier", "PROCUREMENT", "Add new vendors to catalog."),
            ("supplier.update", "Update Supplier", "PROCUREMENT", "Modify vendor data and pricing."),
            ("supplier.delete", "Delete Supplier", "PROCUREMENT", "Remove vendors from system."),
            ("supplier.evaluate", "Evaluate Supplier", "PROCUREMENT", "Assess supplier scores and risk tiers."),
            ("supplier.approve", "Approve Vendor", "PROCUREMENT", "Authorize vendor onboarding and switches."),
            # RFQ & Quotation
            ("rfq.create", "Create RFQ", "PROCUREMENT", "Issue requests for quotation to vendors."),
            ("rfq.read", "View RFQs", "PROCUREMENT", "Browse active and closed RFQs."),
            ("rfq.read_assigned", "View Assigned RFQs", "EXTERNAL", "Suppliers view RFQs sent to their company."),
            ("quotation.create", "Submit Quotation", "EXTERNAL", "Suppliers submit price/delivery proposals."),
            ("quotation.read", "View Quotations", "PROCUREMENT", "Review vendor bids."),
            ("quotation.compare", "Compare Bids", "PROCUREMENT", "Multi-vendor trade-off Pareto comparisons."),
            # Negotiation
            ("negotiation.create", "Initiate Negotiation", "PROCUREMENT", "Start bilateral bargaining sessions."),
            ("negotiation.read", "View Negotiations", "PROCUREMENT", "Inspect bargaining rounds and messages."),
            ("negotiation.respond", "Respond to Negotiation", "EXTERNAL", "Suppliers make counter-offers."),
            ("negotiation.approve", "Approve Contract", "PROCUREMENT", "Sign off on negotiated deal."),
            # Purchase Orders
            ("po.create", "Create Purchase Order", "PROCUREMENT", "Draft new purchase orders."),
            ("po.read", "View Purchase Orders", "PROCUREMENT", "Inspect purchase order catalog."),
            ("po.approve", "Approve Purchase Order", "PROCUREMENT", "Sign off high-value POs."),
            ("po.accept", "Accept Purchase Order", "EXTERNAL", "Suppliers accept incoming POs."),
            # Supply Chain & CNT
            ("inventory.read", "View Inventory", "SUPPLY_CHAIN", "Inspect warehouse stock and safety buffers."),
            ("demand.read", "View Demand", "SUPPLY_CHAIN", "Review consumption rates and forecasts."),
            ("cnt.run", "Run What-If Simulation", "SUPPLY_CHAIN", "Execute CNT counterfactual Monte Carlo simulation."),
            ("decision.read", "View Mitigation Decision", "SUPPLY_CHAIN", "Inspect AI vendor switching proposals."),
            ("decision.approve", "Apply Decision Policy", "PROCUREMENT", "Approve Retain/Negotiate/Switch playbook."),
            # Logistics & Shipping
            ("shipment.read", "Track Shipments", "LOGISTICS", "View in-transit cargo and AIS telemetry."),
            ("shipment.update", "Update Shipment Status", "LOGISTICS", "Modify shipping milestones."),
            ("carrier.read", "View Freight Carriers", "LOGISTICS", "Inspect carrier performance metrics."),
            ("logistics.risk.read", "View Corridor Risks", "LOGISTICS", "Inspect maritime and rail chokepoint alerts."),
            # Customer & Notices
            ("customer.orders.read", "View Client Orders", "OPS", "Monitor impacted client commitments."),
            ("customer.notices.send", "Dispatch Transparency Notice", "OPS", "Send delay advisory emails to clients."),
            ("orders.read_own", "View Own Orders", "EXTERNAL", "External clients view their purchased goods."),
            ("shipments.read_own", "Track Own Shipments", "EXTERNAL", "External clients track arrival times."),
            # Administration & Governance
            ("org.manage", "Manage Organization", "ADMIN", "Configure enterprise parameters and settings."),
            ("dept.manage", "Manage Departments", "ADMIN", "Add, edit, or disable departments."),
            ("user.manage", "Manage Users", "ADMIN", "Create, invite, and assign roles to users."),
            ("role.manage", "Manage Roles", "ADMIN", "Create custom roles and assign permissions."),
            ("audit.read", "View Audit Logs", "ADMIN", "Inspect immutable platform audit trails."),
            ("system.health", "View System Health", "ADMIN", "Telemetry monitoring and agent uptime."),
        ]

        perm_objs = {}
        for code, name, cat, desc in permissions_data:
            p = db.query(PermissionDB).filter(PermissionDB.code == code).first()
            if not p:
                p = PermissionDB(code=code, name=name, category=cat, description=desc)
                db.add(p)
                db.flush()
            perm_objs[code] = p

        # ── 5. Map Permissions to Standard Roles ──
        role_permission_mappings = {
            "ADMIN": list(perm_objs.keys()),  # Admin receives all permissions
            "PROCUREMENT_MANAGER": [
                "supplier.read", "supplier.create", "supplier.update", "supplier.evaluate", "supplier.approve",
                "rfq.create", "rfq.read", "quotation.read", "quotation.compare",
                "negotiation.create", "negotiation.read", "negotiation.approve",
                "po.create", "po.read", "po.approve",
                "cnt.run", "decision.read", "decision.approve",
                "customer.orders.read", "customer.notices.send",
            ],
            "BUYER": [
                "supplier.read", "rfq.create", "rfq.read",
                "quotation.read", "quotation.compare",
                "negotiation.create", "negotiation.read",
                "po.create", "po.read",
                "cnt.run", "decision.read",
            ],
            "SUPPLY_CHAIN_ANALYST": list(perm_objs.keys()),
            "LOGISTICS_MANAGER": [
                "shipment.read", "shipment.update",
                "carrier.read", "logistics.risk.read",
                "cnt.run", "decision.read",
            ],
            "QUALITY_CONTROLLER": [
                "supplier.read", "supplier.evaluate", "po.read", "shipment.read",
            ],
            "FINANCE_ANALYST": [
                "supplier.read", "po.read", "quotation.read", "quotation.compare",
            ],
            "SUPPLIER": [
                "rfq.read_assigned", "quotation.create", "quotation.read",
                "negotiation.read", "negotiation.respond", "po.read", "po.accept",
            ],
            "CUSTOMER": [
                "orders.read_own", "shipments.read_own",
            ],
        }

        for r_name, p_codes in role_permission_mappings.items():
            r = role_objs[r_name]
            for p_code in p_codes:
                p = perm_objs[p_code]
                existing = db.query(RolePermissionDB).filter(
                    RolePermissionDB.role_id == r.id,
                    RolePermissionDB.permission_id == p.id
                ).first()
                if not existing:
                    db.add(RolePermissionDB(role_id=r.id, permission_id=p.id))
        db.flush()

        # ── 6. Create AI Agents Registry ──
        agents_data = [
            ("BUYER_AGENT", "Autonomous Buyer Bargaining Agent", "backend.app.agents.buyer_agent.BuyerAgent", "Formulates bids and optimizes buyer utility functions."),
            ("SUPPLIER_AGENT", "Supplier Concession Agent (Faratin)", "backend.app.agents.supplier_agent.SupplierFaratinAgent", "Calculates concessions and counter-offers using game theory."),
            ("PRICE_ANALYSIS_AGENT", "Price Benchmark Intelligence Agent", "backend.app.agents.price_analysis_agent.PriceAnalysisAgent", "Analyzes unit cost against global historical benchmarks."),
            ("RISK_ASSESSMENT_AGENT", "Multi-Factor Supply Chain Risk Agent", "backend.app.agents.risk_agent.RiskAssessmentAgent", "Calculates composite risk scores across geopolitical corridors."),
            ("LOGISTICS_AGENT", "Global Corridor & Telemetry Agent", "backend.app.agents.logistics_agent.LogisticsAgent", "Evaluates multimodal shipping routes and port delays."),
            ("NEGOTIATION_AGENT", "AI Negotiation Agent", "backend.app.agents.negotiation_agent.NegotiationSupervisorAgent", "Coordinates multi-round bargaining between Buyer and Supplier."),
            ("DECISION_AGENT", "Adaptive Decision Center Agent", "backend.app.agents.decision_agent.AdaptiveDecisionAgent", "Evaluates Retain / Negotiate / Switch mitigation playbooks."),
            ("CUSTOMER_IMPACT_AGENT", "Customer SLA & Transparency Agent", "backend.app.agents.customer_agent.CustomerImpactAgent", "Audits downstream order penalties and drafts schedule notices."),
            ("EXPLANATION_AGENT", "Ollama LLaMA Executive Briefing Agent", "backend.app.agents.explanation_agent.ExplanationAgent", "Synthesizes causal explanations into plain-English business debriefs."),
            ("CNT_SIMULATOR", "Counterfactual Negotiation Twin Engine", "backend.app.cnt.engine.CounterfactualEngine", "Monte Carlo disruption simulation testing alternative supplier choices."),
        ]

        agent_objs = {}
        for code, name, cls_path, desc in agents_data:
            ag = db.query(AIAgentDB).filter(AIAgentDB.code == code).first()
            if not ag:
                ag = AIAgentDB(code=code, name=name, service_class=cls_path, description=desc)
                db.add(ag)
                db.flush()
            agent_objs[code] = ag

        # ── 7. Create AI Capabilities ──
        capabilities_data = [
            ("procurement_intelligence", "Procurement Intelligence", "BUYER_AGENT", "AI discovery and ranking of qualified supplier candidates."),
            ("price_intelligence", "Price & Cost Variance Intelligence", "PRICE_ANALYSIS_AGENT", "Benchmark pricing checks and commodity cost variance tracking."),
            ("supply_risk_analysis", "Supply Chain Risk Assessment", "RISK_ASSESSMENT_AGENT", "Composite risk indexing across weather, chokepoints, and finances."),
            ("negotiation_assistant", "Autonomous Negotiation Assistant", "NEGOTIATION_AGENT", "Automated bilateral bargaining rounds to secure target purchase rates."),
            ("what_if_analysis", "What-If Counterfactual Analysis (CNT)", "CNT_SIMULATOR", "Data-driven disruption simulation testing alternative vendor decisions."),
            ("delivery_impact_analysis", "Logistics & Delivery Impact Analysis", "LOGISTICS_AGENT", "Vessel AIS telemetry and multimodal corridor latency predictions."),
            ("decision_support", "Adaptive Decision Support", "DECISION_AGENT", "Pareto ranking of mitigation actions (Rail Expedite, Air Charter, Dual Sourcing)."),
            ("client_transparency_notices", "Client Transparency & SLA Waiver Engine", "CUSTOMER_IMPACT_AGENT", "Proactive advisory email generation waiving downstream delay fines."),
            ("executive_briefing", "Groq LLaMA Executive Debrief", "EXPLANATION_AGENT", "Plain-English strategic briefings without technical ML terminology."),
        ]

        cap_objs = {}
        for code, name, ag_code, desc in capabilities_data:
            cap = db.query(AICapabilityDB).filter(AICapabilityDB.code == code).first()
            if not cap:
                cap = AICapabilityDB(code=code, name=name, agent_id=agent_objs[ag_code].id, description=desc)
                db.add(cap)
                db.flush()
            cap_objs[code] = cap

        # ── 8. Map AI Capabilities to Roles ──
        role_capability_mappings = {
            "ADMIN": list(cap_objs.keys()),  # Admin has access to all capabilities
            "PROCUREMENT_MANAGER": [
                "procurement_intelligence", "price_intelligence", "supply_risk_analysis",
                "negotiation_assistant", "what_if_analysis", "decision_support",
                "client_transparency_notices", "executive_briefing",
            ],
            "BUYER": [
                "procurement_intelligence", "price_intelligence", "supply_risk_analysis",
                "negotiation_assistant", "what_if_analysis",
            ],
            "SUPPLY_CHAIN_ANALYST": list(cap_objs.keys()),
            "LOGISTICS_MANAGER": [
                "delivery_impact_analysis", "supply_risk_analysis", "what_if_analysis",
            ],
            "QUALITY_CONTROLLER": [
                "supply_risk_analysis",
            ],
            "FINANCE_ANALYST": [
                "price_intelligence", "procurement_intelligence",
            ],
            "SUPPLIER": [
                "negotiation_assistant",
            ],
            "CUSTOMER": [
                "client_transparency_notices",
            ],
        }

        for r_name, c_codes in role_capability_mappings.items():
            r = role_objs[r_name]
            for c_code in c_codes:
                c = cap_objs[c_code]
                existing = db.query(RoleAICapabilityDB).filter(
                    RoleAICapabilityDB.role_id == r.id,
                    RoleAICapabilityDB.capability_id == c.id
                ).first()
                if not existing:
                    db.add(RoleAICapabilityDB(role_id=r.id, capability_id=c.id))
        db.flush()

        # ── 9. Seed Default Users with PBKDF2 Password Hashes ──
        default_pwd_hash = get_password_hash("enterprise_pass_2026")

        users_data = [
            {
                "email": "admin@rimberio.ai",
                "name": "Alexander Vance (Enterprise Platform Administrator)",
                "role": "ADMIN",
                "dept": "ADMIN",
                "org": primary_org.id,
            },
            {
                "email": "procurement.manager@rimberio.ai",
                "name": "Marcus Aurelius Vance (VP of Global Procurement)",
                "role": "PROCUREMENT_MANAGER",
                "dept": "PROC",
                "org": primary_org.id,
            },
            {
                "email": "buyer@rimberio.ai",
                "name": "Priya Sharma (Senior Procurement Specialist)",
                "role": "BUYER",
                "dept": "PROC",
                "org": primary_org.id,
            },
            {
                "email": "elena.rostova@rimberio.ai",
                "name": "Elena Rostova (Lead Enterprise Buyer)",
                "role": "BUYER",
                "dept": "PROC",
                "org": primary_org.id,
            },
            {
                "email": "analyst@rimberio.ai",
                "name": "David Chen (Lead Supply Chain & Risk Analyst)",
                "role": "SUPPLY_CHAIN_ANALYST",
                "dept": "SCM",
                "org": primary_org.id,
            },
            {
                "email": "logistics@rimberio.ai",
                "name": "Captain Henrik Lindholm (Global Freight Director)",
                "role": "LOGISTICS_MANAGER",
                "dept": "LOG",
                "org": primary_org.id,
            },
            {
                "email": "quality@rimberio.ai",
                "name": "Dr. Beatrice Dupont (Chief Quality Officer)",
                "role": "QUALITY_CONTROLLER",
                "dept": "QA",
                "org": primary_org.id,
            },
            {
                "email": "finance@rimberio.ai",
                "name": "Julian Thorne (Procurement Controller)",
                "role": "FINANCE_ANALYST",
                "dept": "FIN",
                "org": primary_org.id,
            },
            {
                "email": "supplier@apexlogistics.com",
                "name": "Kenji Sato (Director, Apex Global Logistics)",
                "role": "SUPPLIER",
                "dept": "PROC",
                "org": primary_org.id,
            },
            {
                "email": "customer@boeing.com",
                "name": "Rachel Adams (Procurement Director, Boeing Aviation)",
                "role": "CUSTOMER",
                "dept": "OPS",
                "org": primary_org.id,
            },
        ]

        for u in users_data:
            existing = db.query(UserDB).filter(UserDB.email == u["email"]).first()
            role = role_objs[u["role"]]
            dept = dept_objs.get(u["dept"])

            if not existing:
                user = UserDB(
                    email=u["email"],
                    password_hash=default_pwd_hash,
                    full_name=u["name"],
                    role_id=role.id,
                    organization_id=u["org"],
                    department_id=dept.id if dept else None,
                    status="ACTIVE",
                    is_active=True,
                )
                db.add(user)
                db.flush()
                # Also add to user_roles
                db.add(UserRoleDB(user_id=user.id, role_id=role.id))
            else:
                existing.password_hash = default_pwd_hash
                existing.organization_id = u["org"]
                existing.department_id = dept.id if dept else None
                existing.role_id = role.id

        # Update existing business entities with primary_org.id if missing
        db.query(SupplierDB).filter(SupplierDB.organization_id == None).update(
            {"organization_id": primary_org.id}, synchronize_session=False
        )
        db.query(ProductDB).filter(ProductDB.organization_id == None).update(
            {"organization_id": primary_org.id}, synchronize_session=False
        )
        db.query(CustomerDB).filter(CustomerDB.organization_id == None).update(
            {"organization_id": primary_org.id}, synchronize_session=False
        )
        db.query(WarehouseDB).filter(WarehouseDB.organization_id == None).update(
            {"organization_id": primary_org.id}, synchronize_session=False
        )
        db.query(CarrierDB).filter(CarrierDB.organization_id == None).update(
            {"organization_id": primary_org.id}, synchronize_session=False
        )

        db.commit()
        print(">>> Enterprise multi-tenant hierarchy and RBAC seed completed successfully.")
        return True
    except Exception as e:
        db.rollback()
        print(f">>> Enterprise seeding failed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_enterprise_hierarchy()
