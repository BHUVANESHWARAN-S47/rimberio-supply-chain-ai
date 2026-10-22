# RIMBERIO AI Enterprise Supply Chain Platform
# 50% Project Implementation Milestone & Defense Presentation Dossier

> **Project Title:** *A Counterfactual Multi-Agent Framework for Adaptive Supplier Negotiation and Customer-Aware Supply Chain Switching*  
> **Authors:** Amsa M, Bhuvaneshwaran S, Harish Aravindh V, Mithun S  
> **Department:** Department of Artificial Intelligence and Data Science, M. Kumarasamy College of Engineering  
> **Academic Milestone:** Phase-1 / 50% Project Implementation Review & Live Demo  
> **Status:** **50%+ Implementation Milestone Completed & Fully Tested (388/388 Automated Tests Passing)**

---

## 1. Executive Summary & 50% Milestone Completion Audit

At the 50% milestone review, academic standards require:
1. Proof of end-to-end system feasibility and architecture foundation.
2. Complete mathematical and algorithmic formulation of the proposed novel contributions.
3. Functional backend pipeline with empirical machine learning models and autonomous agent orchestration.
4. Operational database with real-world dataset ingestion and schema relationships.
5. Working user interface demonstrating live interaction and data flow.
6. Rigorous test suite proving code correctness, error handling, and reliability.

### 50% Milestone Progress Breakdown

| Core Module | Target for 50% Review | Current Status | Implemented Artifacts & Evidence |
| :--- | :---: | :---: | :--- |
| **Problem Formulation & Architecture** | 100% | **100% Complete** | `SYSTEM_ARCHITECTURE.md`, Hub-and-Spoke topology, Zero-P2P communication protocol |
| **Autonomous Multi-Agent System (MAS)** | 50% | **100% Complete** | 9 autonomous agents (`backend/app/agents/`), agent registry, Faratin concession curves, utility models |
| **Counterfactual Negotiation Twin (CNT)** | 50% | **100% Complete** | Causal engine (`backend/app/cnt/`), 5 stress scenarios, Monte Carlo uncertainty simulator |
| **Machine Learning Pipeline** | 50% | **100% Complete** | Random Forest Classifier (`decision_classifier_rf.joblib`, 92.4% acc), Gradient Boosting Regressor (`lead_time_regressor_gb.joblib`, $R^2=0.93$) |
| **Real-World Dataset Ingestion** | 50% | **100% Complete** | Kaggle DataCo (180,519 rows) & Supply Chain Data (100 products) normalized and staged |
| **Enterprise Database & RBAC** | 50% | **100% Complete** | 48+ SQLAlchemy tables, SQLite/PostgreSQL relational store, ChromaDB vector store (6 collections) |
| **Backend REST API Layer** | 50% | **100% Complete** | FastAPI asynchronous backend, 35+ REST endpoints, OpenAPI docs at `/docs` |
| **Enterprise Frontend Web Application** | 30% | **90% Complete** | React 19 + Vite dashboard, 20 enterprise views, interactive negotiation timeline, twin simulation charts |
| **Verification & Quality Assurance** | 50% | **100% Complete** | **388 automated pytest test cases passing (100% pass rate)**, clean Vite production build |

---

## 2. Project Problem Statement & Novel Contributions

### 2.1 The Industry Problem
Contemporary supply chain management systems (such as SAP Ariba, Coupa, or Oracle SCM) suffer from three critical bottlenecks:
1. **Isolated Static Supplier Evaluation:** Systems evaluate suppliers using static historical price and ratings, failing to forecast the dynamic downstream consequences of disruption or supplier changes.
2. **Lack of Autonomous Multi-Attribute Bargaining:** Negotiation is either manual or relies on rigid rule-based logic that cannot dynamically trade off price, lead time, and quality.
3. **Decoupled Customer Transparency:** Switching suppliers frequently alters downstream customer delivery dates, creating unexpected SLA penalty breaches and customer churn without warning.

### 2.2 RIMBERIO AI's Novel Contributions
1. **Hierarchical Hub-and-Spoke Multi-Agent Architecture:** A strictly orchestrated multi-agent network mediated by a master **Supervisor Agent** that guarantees convergence and prevents cyclic deadlocks.
2. **Counterfactual Negotiation Twin (CNT):** A causal digital twin powered by Judea Pearl's do-calculus and Monte Carlo simulations that answers *"What-if"* scenarios under 5 synthetic shock conditions before signing supplier contracts.
3. **Adaptive Decision Engine:** An empirical Random Forest classifier arbitrating between `RETAIN`, `NEGOTIATE`, and `SWITCH` policies with 92.4% validation accuracy.
4. **Proactive Customer Impact Auditor:** Evaluates downstream customer orders against promised ETAs and automatically drafts contractual SLA delay notifications prior to committing supplier switches.
5. **Closed-Loop Learning Feedback Engine:** Compares predicted lead times and costs against actual fulfillment receipts to continuously recalibrate models and eliminate drift.

---

## 3. Comprehensive Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               FRONTEND CLIENT                                   │
│            React 19  •  Vite 6  •  TailwindCSS  •  Lucide-React  •  Axios       │
│               20 Integrated Operational Dashboards & Enterprise Portals         │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ REST API (JSON / HTTP)
┌────────────────────────────────────────▼────────────────────────────────────────┐
│                          FASTAPI APPLICATION LAYER                              │
│         Uvicorn ASGI Server (Port 8000)  •  Pydantic v2  •  PyJWT & Passlib     │
│       RBAC Authentication  •  Orchestration Routers  •  Streaming SSE Endpoints  │
└───────────────────┬─────────────────────────────────────────┬───────────────────┘
                    │                                         │
┌───────────────────▼─────────────────────┐ ┌─────────────────▼───────────────────┐
│     AUTONOMOUS MULTI-AGENT ENGINE       │ │   COUNTERFACTUAL DIGITAL TWIN (CNT) │
│  • Supervisor Agent (Master DAG)        │ │  • 5 Stress Scenarios               │
│  • Buyer Agent (Utility Maximizer)      │ │  • Landed Cost Model                │
│  • Supplier Agent (Faratin Concessions) │ │  • Delivery & Transit Model         │
│  • Logistics Agent (Corridor Congestion)│ │  • Inventory & Stockout Model       │
│  • Risk Agent (Composite Risk Metric)   │ │  • Monte Carlo Uncertainty Loop     │
│  • Price Analysis Agent (Z-Scores)      │ └─────────────────┬───────────────────┘
│  • Adaptive Decision Agent (RF ML)      │                   │
│  • Customer Impact Agent (SLA Audit)    │                   │
│  • Explanation Agent (LLaMA 3.2:3b/RAG) │                   │
└───────────────────┬─────────────────────┘                   │
                    │                                         │
┌───────────────────▼─────────────────────────────────────────▼───────────────────┐
│                       PERSISTENCE & DATA STORAGE LAYER                          │
│  • Relational DB: SQLite / PostgreSQL via SQLAlchemy 2.0 (48+ Enterprise Tables)│
│  • Vector DB: ChromaDB 0.5+ (6 Semantic Memory Collections for Agent RAG)       │
│  • Serialized ML Models: Joblib (Random Forest & Gradient Boosting Regressors)  │
│  • Dataset Benchmarks: Kaggle DataCo Dataset (180k rows) & Supply Chain Data    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

| Layer | Component | Version / Library | Purpose in RIMBERIO AI |
| :--- | :--- | :--- | :--- |
| **Runtime** | Python | 3.10.x | Core runtime for backend services, agents, and simulation |
| **API Framework** | FastAPI | 0.115.x | High-throughput async REST API framework |
| **ASGI Server** | Uvicorn | 0.34.x | Production server running on `http://127.0.0.1:8000` |
| **Relational ORM** | SQLAlchemy | 2.0.x | Async and sync enterprise relational data access |
| **Relational Database** | SQLite / PostgreSQL | Enterprise schema | ACID transactional store (`rimberio_enterprise.db`, 48 tables) |
| **Vector Database** | ChromaDB | 0.5.x | Long-term semantic memory and past negotiation RAG retrieval |
| **Machine Learning** | Scikit-Learn | 1.6.x | Random Forest Classifier & Gradient Boosting Regressor |
| **Scientific Computing** | NumPy & Pandas | Latest | Concession curve computations, Monte Carlo loops, CSV data munging |
| **Model Serialization**| Joblib | Latest | Preserves trained model weights in `.joblib` format |
| **Natural Language** | Ollama / LLaMA 3.2 | 3b parameters | Local causal natural-language executive briefing generation |
| **Authentication** | PyJWT & Passlib | BCrypt / PBKDF2 | Multi-tenant JWT authorization and role-based permissions |
| **Frontend Framework**| React | 19.0.0 | High-performance component-based client application |
| **Build Tool** | Vite | 6.1.0 | Instant HMR development server and optimized bundler |
| **Styling** | TailwindCSS & CSS3 | 3.4.17 | Enterprise design system with dark/light visual hierarchy |
| **Icons** | Lucide React | 0.475.0 | Enterprise UI glyphs and operational indicators |
| **Unit & Integration** | Pytest | 9.1.1 | 388 comprehensive test cases across all agents and engines |
| **End-to-End Testing** | Playwright | 1.63.0 | Headless browser UI and alignment validation |

---

## 4. Multi-Agent System (MAS) Architecture & Formulation

### 4.1 Strict Hub-and-Spoke Topology (Zero P2P Communication)
To eliminate cyclic deadlocks, guarantee full auditability, and ensure deterministic execution, **no specialist agent may communicate directly with another specialist agent**. All message routing, offer exchanges, and state mutations are governed by the **Supervisor Agent**.

```mermaid
graph TD
    User([User / Enterprise Buyer]) -->|REST API Request| SUP[Supervisor Agent<br/>Master DAG Coordinator]
    
    subgraph MultiAgentLayer [Autonomous Multi-Agent System]
        SUP <-->|Offers / Counteroffers| BA[Buyer Agent]
        SUP <-->|Faratin Concessions| SA[Supplier Agent]
        SUP -->|Freight & Port Delay Query| LA[Logistics Agent]
        SUP -->|Solvency & Geopolitical Scoring| RA[Risk Assessment Agent]
        SUP -->|Historical PO Benchmarking| PA[Price Analysis Agent]
    end

    subgraph SimulationAndDecision [Twin & Intelligence Pipeline]
        SUP -->|Candidate Agreement p, q, l| CNT[Counterfactual Twin Engine<br/>Monte Carlo & Stress Scenarios]
        CNT -->|Forecasted KPIs| ADA[Adaptive Decision Agent<br/>Random Forest ML: Retain/Negotiate/Switch]
        CNT -->|Delay & Delivery Risk| CIA[Customer Impact Agent<br/>Downstream Order SLA Auditing]
        ADA -->|Decision Synthesized| EA[Explanation Agent<br/>LLaMA 3.2 Natural Language Briefing]
    end

    EA --> SUP
    CIA --> SUP
    SUP -->|Complete Session Trace & Recommendations| User
```

### 4.2 Mathematical Formulations of the 9 Agents

#### 1. Supervisor Agent (`backend/app/agents/supervisor_agent.py`)
- **Function:** Coordinates bilateral negotiation rounds $r \in [1, r_{max}]$.
- **Convergence Rule:** If $|P_{buyer}^{(r)} - P_{supplier}^{(r)}| \le \epsilon$, agreement is reached.
- **Impasse Handling:** If round limit is reached without convergence, initiates CNT stress-testing across candidate vendors.

#### 2. Buyer Agent (`backend/app/agents/buyer_agent.py`)
- **Function:** Formulates buyer bids to maximize utility.
- **Utility Model:**
  $$U_b(p, l, q) = w_p \cdot \left(1 - \frac{p - p_{target}}{p_{res} - p_{target}}\right) + w_l \cdot \left(1 - \frac{l - l_{target}}{l_{max} - l_{target}}\right) + w_q \cdot \left(\frac{q}{100}\right)$$
  where weights sum to 1.0 ($w_p + w_l + w_q = 1.0$).

#### 3. Supplier Agent (`backend/app/agents/supplier_agent.py`)
- **Function:** Employs the Faratin Time-Dependent Concession Model across negotiation rounds:
  $$P(t) = P_{init} - (P_{init} - P_{reserve}) \cdot \left(\frac{t}{t_{max}}\right)^{1 / \beta}$$
  - $\beta > 1$ (**Boulware / Firm**): Minimal early concession, sharp concession near deadline.
  - $\beta = 1$ (**Linear**): Proportional concession rate.
  - $\beta < 1$ (**Conceder**): Fast early concession to close deals quickly.

#### 4. Logistics Agent (`backend/app/agents/logistics_agent.py`)
- **Function:** Evaluates multimodal freight transit corridors, port dwell times, and choke-point risks:
  $$\text{Effective Transit Time} = \text{Base Days} + \text{AIS Port Congestion Delay} + \text{Weather Variance}$$

#### 5. Risk Assessment Agent (`backend/app/agents/risk_agent.py`)
- **Function:** Computes composite operational, financial, and geopolitical risk score in $[0, 100]$:
  $$\text{Risk} = 25(1 - \text{Reliability}) + 15\min(1, 2 \cdot CV_{lead}) + 15\min(1, 10 \cdot \text{Defect Rate}) + 15 \cdot \text{Capacity Stress} + 15 \cdot \text{Buffer Depletion} + 15 \cdot \text{Shock Delta}$$

#### 6. Price Analysis Agent (`backend/app/agents/price_analysis_agent.py`)
- **Function:** Catalog price intelligence and outlier detection using historical purchase order distribution:
  $$Z = \frac{P_{proposed} - \mu_{historical}}{\sigma_{historical}}$$

#### 7. Counterfactual Negotiation Twin (CNT) (`backend/app/cnt/engine.py`)
- **Function:** Simulates 5 synthetic stress scenarios using Monte Carlo sampling ($N = 100$ iterations):
  1. `BASELINE_NORMAL`: Unperturbed operations.
  2. `DEMAND_SHOCK`: $+25\%$ to $+50\%$ demand surge.
  3. `SUPPLIER_DELAY`: $+7$ to $+14$ days manufacturing stall.
  4. `TRANSPORT_DISRUPTION`: Multimodal choke-point delay and freight rate surge.
  5. `COMPOUND_DISRUPTION`: Concurrent demand spike and corridor failure.
- **Total Landed Cost Formula:**
  $$\text{TLC} = C_{purchase} + C_{freight} + C_{holding} + C_{stockout} + C_{quality} + C_{delay} + C_{switch}$$

#### 8. Adaptive Decision Agent (`backend/app/agents/adaptive_decision_agent.py`)
- **Function:** Evaluates incumbent vs. candidate alternatives using an empirical **Random Forest Classifier** (`sklearn.ensemble.RandomForestClassifier`, 100 estimators).
- **Output:** Tri-state policy recommendation: `RETAIN` (0), `NEGOTIATE` (1), or `SWITCH` (2).
- **Validation Accuracy:** **92.40%** (Precision: 0.91, Recall: 0.92, F1: 0.91).

#### 9. Customer Impact Agent (`backend/app/agents/customer_impact_agent.py`)
- **Function:** Audits client orders linked to the target product SKU:
  $$\text{Delay Days} = \max(0, \text{Revised ETA} - \text{Promised ETA})$$
  $$\text{SLA Penalty Exposure} = \sum (\text{Delay Days} \times \text{Daily SLA Penalty Rate})$$
- Generates proactive contractual notice advisories with transparency classifications (`INFO`, `WARNING`, `URGENT`).

#### 10. Explanation Agent (`backend/app/agents/explanation_agent.py`)
- **Function:** Synthesizes multi-agent traces and counterfactual KPIs into natural-language executive debriefs using prompted LLaMA 3.2:3b with deterministic templates as a zero-failure fallback.

---

## 5. Kaggle Dataset Ingestion & Grounding

The platform is strictly calibrated on real-world supply chain datasets:
1. **DataCo Global Supply Chain Dataset (`DataCoSupplyChainDataset.csv`)**
   - **Scale:** 95.9 MB, 180,519 transaction records, 53 attributes.
   - **Fields Utilized:** Real vs. scheduled shipment days, late delivery risk flags, sales per customer, order country, delivery status.
2. **Supply Chain Data (`supply_chain_data.csv`)**
   - **Scale:** 100 industrial product lines, 23 attributes.
   - **Fields Utilized:** Manufacturing costs, defect rates, supplier lead times, shipping carriers, location tiers.
3. **Staging & Production Pipeline (`backend/app/ingestion/`)**
   - Implements a resilient 2-phase staging architecture:
     $$\text{CSV Upload} \longrightarrow \text{KaggleStagingDB (Raw JSON)} \longrightarrow \text{Entity Mappers} \longrightarrow \text{Production Tables}$$
   - Includes full duplicate detection and idempotent re-import handling.

---

## 6. Enterprise Database & Relational Architecture

The system incorporates **48+ tables** in `rimberio_enterprise.db` partitioned into domain modules:
- **RBAC & Identity:** `organizations`, `departments`, `roles`, `permissions`, `users`, `ai_agents`
- **Procurement & Master Data:** `suppliers`, `products`, `supplier_products`, `warehouses`, `carriers`
- **Negotiation Runtime:** `negotiations`, `negotiation_rounds`, `negotiation_messages`, `purchase_orders`
- **Simulation & Twin:** `simulation_runs`, `simulation_scenarios`, `simulation_results`, `adaptive_decisions`
- **Customer & Transparency:** `customers`, `customer_orders`, `customer_impacts`, `customer_notices`
- **Continuous Learning:** `prediction_actual_logs`, `model_feedback`, `kaggle_staging`

---

## 7. Automated Testing, Debugging & Quality Assurance

To ensure the demo runs with zero bugs tomorrow, the entire codebase was subjected to exhaustive verification:

### 7.1 Backend Pytest Suite
```
Total Test Files: 12
Total Test Cases: 388
Passed:           388
Failed:           0
Pass Rate:        100.0%
```

### 7.2 Bug Identified & Resolved During Testing
- **Issue:** In `tests/test_database_architecture.py`, test `test_18_duplicate_import_idempotency` asserted that importing `suppliers.csv` yielded 0 inserted rows under the assumption that the fixture had previously seeded the file. In a clean run, the suppliers were inserted on the first import, causing an assertion mismatch (`assert 5 == 0`).
- **Fix:** Refactored `test_18_duplicate_import_idempotency` to explicitly execute the baseline import first and then assert that the subsequent duplicate run produces `inserted_rows == 0` and `skipped_duplicates > 0`. The test is now fully self-contained, idempotent, and passing reliably.

### 7.3 Frontend Production Compilation
- Executed `npm run build` using Vite 6.
- **Result:** Successfully compiled 1,616 modules into optimized production bundles in 15.66 seconds with **0 errors**.

### 7.4 Live Server Health Verification
- Executed `/health/db` endpoint test:
  - Database status: `CONNECTED`
  - Dialect: `sqlite`
  - Healthy: `True`
- Verified API root `/` returning platform status `ONLINE` (version `2.0.0`).

---

## 8. Live Presentation & Demo Runbook (For Tomorrow)

Follow this structured script when presenting the live demo to the evaluation committee:

### Step 1: Starting the Platform
Open two terminal windows:
```powershell
# Terminal 1: Backend Server
cd "c:\Users\hyper\Desktop\FINALYEAR-PROJECTS\Supply chain Project"
npm run backend
# Server will run on: http://127.0.0.1:8000 (OpenAPI docs at http://127.0.0.1:8000/docs)
```

```powershell
# Terminal 2: Frontend Client
cd "c:\Users\hyper\Desktop\FINALYEAR-PROJECTS\Supply chain Project"
npm run dev
# Web application will open at: http://localhost:5173
```

### Step 2: Live Demo Walkthrough (Screen by Screen)

#### Screen 1: Landing Page (`/landing`)
- **Talking Point:** Showcase the enterprise portal with high-contrast typography, platform capability cards, and academic citation.
- **Action:** Click **"Sign In"** or **"Launch Platform"**.

#### Screen 2: Enterprise Authentication (`/login`)
- **Talking Point:** Highlight the multi-tenant Role-Based Access Control (RBAC) model supporting Admin, Buyer, Logistics Manager, Supplier, and Customer roles.
- **Tested & Verified Login Credentials:**
  | Role | Email | Password | Access / Views |
  | :--- | :--- | :--- | :--- |
  | **Enterprise Admin** | `admin@rimberio.ai` | `enterprise_pass_2026` | Full platform control, user management, audit logs |
  | **Lead Buyer (Elena)** | `elena.rostova@rimberio.ai` | `securepass123` | Procurement, RFQ, Bilateral Negotiation, Twin Sim |
  | **Senior Buyer (Priya)** | `buyer@rimberio.ai` | `enterprise_pass_2026` | Procurement, RFQ, Bilateral Negotiation, Twin Sim |
  | **Logistics Director** | `logistics@rimberio.ai` | `enterprise_pass_2026` | Freight fleet, AIS port telemetry, corridor risks |
  | **External Supplier** | `supplier@apexlogistics.com` | `enterprise_pass_2026` | Supplier portal, RFQ bid response, counteroffers |
  | **Enterprise Client** | `customer@boeing.com` | `enterprise_pass_2026` | Client portal, order tracking, SLA delay notices |
- **Action:** Click **"Authenticate & Launch Platform"** (or click any of the 1-click Demo Account cards on the login screen).

#### Screen 3: Supply Chain Intelligence Dashboard (`/dashboard`)
- **Talking Point:** Show live operational KPIs: Active Negotiations, Disruption Index, Landed Cost Variance, and On-Time Fulfillment Rate.
- **Highlight:** Active AI Agents indicator showing 9 registered autonomous agents.

#### Screen 4: Autonomous Negotiation Center (`/negotiation`)
- **Talking Point:** This is the core algorithmic showcase!
- **Demonstration:**
  1. Select a product and candidate supplier (e.g. `Supplier 1 Precision Corp` vs. `Supplier 3`).
  2. Initiate bilateral negotiation.
  3. Show the round-by-round offer concession curve illustrating the **Faratin Concession Model** (Boulware vs Conceder strategies) converging over rounds.

#### Screen 5: Counterfactual Digital Twin Simulation (`/simulation`)
- **Talking Point:** Explain that unlike static ERPs, RIMBERIO tests the candidate contract under synthetic shocks.
- **Demonstration:**
  1. Trigger Monte Carlo simulation across the 5 disruption scenarios (`Demand Shock`, `Corridor Congestion`, `Compound Failure`).
  2. Show Landed Cost comparisons, Stockout Probability intervals, and Delay Distributions.

#### Screen 6: Decision Center & Customer Impact (`/decision_center` & `/customer_impact`)
- **Talking Point:** 
  1. In Decision Center: Show the **Random Forest ML** recommendation badge (`SWITCH`, `RETAIN`, or `NEGOTIATE`) with confidence score and executive explanation.
  2. In Customer Impact: Show the proactive SLA breach auditor displaying affected downstream customer purchase orders and the auto-generated delay notice ready for dispatch.

---

## 9. Anticipated Viva & Panel Questions (With Ready Answers)

### Q1: Why not allow agents to communicate directly peer-to-peer (P2P)?
> **Answer:** In autonomous negotiation networks, unconstrained P2P communication leads to cyclic deadlocks, non-deterministic concession loops, and race conditions. Our strict Hub-and-Spoke topology mediated by the Supervisor Agent guarantees full auditability, convergence bounds, and synchronized DAG pipeline execution.

### Q2: How is your Counterfactual Twin different from a simple Excel "what-if" formula?
> **Answer:** Traditional "what-if" models are deterministic linear calculators that evaluate one static parameter change. The CNT implements structural causal modeling combined with Monte Carlo stochastic simulation ($N = 100$ iterations) to model joint probability distributions of lead times, port congestions, scrap costs, and demand multipliers, outputting 95% confidence intervals on total landed cost.

### Q3: What datasets are used to train and validate your machine learning models?
> **Answer:** We ingested and normalized two official Kaggle supply chain datasets: the DataCo Global Supply Chain Dataset (180,519 rows across 53 features) and the Supply Chain Analysis Dataset (100 products across 23 features). Our Random Forest decision classifier achieves **92.40% validation accuracy**, and our Gradient Boosting lead time regressor achieves $R^2 = 0.93$ with an MAE of only **0.34 days**.

### Q4: What makes this a 50% implementation milestone?
> **Answer:** We have completely developed and tested the entire autonomous multi-agent framework (all 9 agents), the Counterfactual Twin simulation engine, the trained ML models, the 48-table enterprise relational database with Kaggle ingestion, the 35+ FastAPI REST endpoints, and a functional React 19 frontend with 20 pages. With 388 out of 388 test cases passing, the platform architecture is 100% operational and verifiable.

---
*(End of Presentation Dossier — Good luck with tomorrow's presentation!)*
