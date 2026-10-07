# RIMBERIO — Enterprise Autonomous Supply Chain Digital Twin
> **A Counterfactual Multi-Agent Framework for Adaptive Supplier Negotiation & Customer-Aware Supply Chain Switching**

[![React](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Vite-d946ef)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20(Python%203.10)-000000)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/Database-SQLAlchemy%20%2B%20SQLite-d946ef)](https://www.sqlalchemy.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML%20Engine-Scikit--Learn%20%2B%20NumPy-000000)](https://scikit-learn.org/)
[![Playwright](https://img.shields.io/badge/Testing-Playwright%20E2E%20(100%25%20Green)-d946ef)](https://playwright.dev/)

---

## 1. Executive Product Overview

**RIMBERIO** is an enterprise-grade autonomous supply chain digital twin that bridges multi-agent autonomous negotiation, causal counterfactual simulation, adaptive supplier switching, and automated customer transparency.

Unlike traditional static dashboards, RIMBERIO operates as a **self-driving twin**:
1. **Detects Disruptions**: Continuously monitors maritime corridors and global chokepoints (e.g., Suez, Panama, Malacca Strait).
2. **Evaluates Alternatives**: Benchmarks candidate vendors using multi-criteria weighted scoring (MCDA).
3. **Autonomous Negotiation**: Deploys Buyer, Supplier, and Logistics agents to negotiate spot contracts using time-dependent concession curves.
4. **Counterfactual Simulation (CNT)**: Evaluates *"what-if"* causal scenarios using stochastic Monte Carlo DAG sampling.
5. **Customer Transparency**: Audits downstream customer backlogs and dispatches automated personalized delivery advisories.
6. **Continuous Learning**: Evaluates prediction error ($\text{MAE}$, $\text{RMSE}$) and maintains an online Retain/Negotiate/Switch confusion matrix.

---

## 2. Directory Structure & Organization

The repository is organized into distinct, enterprise-standard directories:

```
Supply chain Project/
├── backend/                       # Python FastAPI Backend & ML Engines
│   ├── agents/                   # Dedicated Mathematical & Agentic AI Models
│   │   ├── admin_auditor_agent.py   # Scikit-learn Classifier & Confusion Matrix
│   │   ├── buyer_agent.py           # Multi-Attribute Utility & Boulware Concession
│   │   ├── counterfactual_twin.py   # Causal Monte Carlo DAG Engine (1000 trials)
│   │   ├── customer_impact_agent.py # SLA Contract Penalty & Churn Risk Model
│   │   ├── logistics_agent.py       # Chokepoint Queueing & Transit Variance
│   │   └── supplier_agent.py        # Margin Floors & Volume Discount Curves
│   ├── data/                     # Persistent Database & Dataset Storage
│   │   ├── rimberio_enterprise.db   # SQLite Relational Database (SQLAlchemy)
│   │   ├── suppliers.csv            # Vendor catalog & risk indices
│   │   ├── orders.csv               # Active enterprise customer orders
│   │   ├── fulfillment_history.csv  # Historical ground-truth fulfillment records
│   │   ├── kaggle_dataco_sample.csv # 53-col Kaggle DataCo benchmark sample
│   │   └── kaggle_supply_chain_sample.csv # Kaggle Supply Chain Analysis sample
│   ├── database/                 # Relational Persistence Layer
│   │   ├── database.py              # Engine configuration & SessionLocal
│   │   ├── models.py                # SQLAlchemy ORM Tables
│   │   └── seed_db.py               # Auto-seeder from Kaggle datasets
│   ├── models/                   # Pydantic v2 API Schemas & DTOs
│   │   └── schemas.py
│   ├── routers/                  # Modular FastAPI REST API Endpoints
│   │   ├── agents.py                # /api/agents (Negotiation sessions & steps)
│   │   ├── customization.py         # /api/customization (Weights & prompts)
│   │   ├── customer_impact.py       # /api/customer-impact (Orders & notices)
│   │   ├── data_router.py           # /api/data (Kaggle & CSV upload endpoints)
│   │   ├── decision.py              # /api/decision (Retain/Negotiate/Switch)
│   │   ├── learning.py              # /api/learning (Metrics & recalibration)
│   │   ├── simulation.py            # /api/simulation (Counterfactual runs)
│   │   └── suppliers.py             # /api/suppliers (Weighted rankings)
│   ├── services/                 # Business Logic & Orchestration Services
│   │   ├── agents_engine.py
│   │   ├── counterfactual_twin.py
│   │   ├── customer_impact.py
│   │   ├── customization_store.py
│   │   ├── data_manager.py
│   │   ├── decision_engine.py
│   │   └── learning_feedback.py
│   ├── main.py                   # FastAPI Application Entrypoint
│   ├── requirements.txt          # Python Package Dependencies
│   └── README.md                 # Backend Quickstart & Service Docs
│
├── docs/                          # Architecture & Technical Documentation
│   ├── BACKEND_ARCHITECTURE.md   # C4 Architecture Blueprint & Specs
│   ├── DESIGN.md                 # UI/UX Drafting Table Design Specifications
│   ├── ENTERPRISE_FULLSTACK_PLAN.md # Full-Stack Implementation Roadmap
│   ├── KAGGLE_DATASET_INTEGRATION.md # Kaggle DataCo & Supply Chain Guide
│   └── RIMBERIO_PAGE_DETAILS.md  # Complete 9-Step Research Page Map
│
├── material/                      # Academic Research & Reference Materials
│   ├── Final_paper.docx          # Published Research Paper Manuscript
│   ├── PROJECT REVIEW - 2.pdf    # Academic Project Defense Presentation
│   ├── material_paper_text.txt   # Normalized Paper Text Transcript
│   └── colorpattate.png          # Palette Swatch Asset
│
├── public/                        # Static Browser Assets
│   └── vite.svg
│
├── src/                           # React 19 Frontend (Vite + Tailwind CSS)
│   ├── components/               # Enterprise UI Components
│   │   ├── Header.jsx               # Navigation bar, role switcher, alerts
│   │   └── Sidebar.jsx              # 8-step pipeline navigation & node status
│   ├── context/                  # React State Context
│   │   └── AppContext.jsx           # Global state, authentication, active roles
│   ├── pages/                    # Application Views (9-Step Pipeline)
│   │   ├── LandingPage.jsx          # Public product landing page
│   │   ├── DashboardPage.jsx        # Real-time intelligence & global radar map
│   │   ├── NegotiationPage.jsx      # Multi-agent negotiation terminal
│   │   ├── SimulationPage.jsx       # Counterfactual simulation playground
│   │   ├── SupplierPage.jsx         # Supplier catalog & weighted evaluation
│   │   ├── DecisionCenterPage.jsx   # Adaptive Retain/Negotiate/Switch center
│   │   ├── CustomerImpactPage.jsx   # Order delay audit & templated notices
│   │   ├── LearningFeedbackPage.jsx # Confusion matrix & model recalibration
│   │   ├── ReportsPage.jsx          # Platform audit logs & architecture
│   │   ├── LoginPage.jsx            # Enterprise authentication
│   │   ├── RegisterPage.jsx         # Organization provisioning
│   │   └── ForgotPasswordPage.jsx   # Credential recovery
│   ├── services/                 # Frontend API Client
│   │   └── api.js                   # Centralized API service with fallbacks
│   ├── utils/                    # Frontend Helper Functions
│   │   └── exportProject.js         # Complete source code export utility
│   ├── App.jsx                   # Root Component & Page Switcher
│   ├── index.css                 # Light Magenta Design System Tokens
│   └── main.jsx                  # React DOM Entrypoint
│
├── tests/                         # Automated End-to-End Test Suite
│   └── ui-alignment-buttons.spec.js # Playwright E2E UI & Button Tests
│
├── package.json                   # Node.js NPM Scripts & Dependencies
├── playwright.config.js           # Playwright Test Runner Configuration
├── tailwind.config.js             # Tailwind CSS Configuration
└── vite.config.js                 # Vite Bundler Configuration
```

---

## 3. Technology Stack

| Layer | Technologies | Role |
|---|---|---|
| **Frontend UI** | React 19, Vite, Tailwind CSS, Lucide Icons | Responsive drafting table UI with Light Magenta accent palette. |
| **Backend API** | Python 3.10+, FastAPI, Uvicorn | High-performance async ASGI server with OpenAPI documentation. |
| **Database** | SQLite, SQLAlchemy ORM | Relational persistence for suppliers, orders, sessions, and telemetry. |
| **Machine Learning** | Scikit-learn, NumPy, Pandas | Random Forest decision classifier, MAE/RMSE calculation, Monte Carlo. |
| **Data Ingestion** | Pandas, CSV / JSON Parsers | Native support for Kaggle DataCo (53 cols) and Supply Chain Analysis. |
| **Testing** | Playwright E2E Test Suite | Automated regression testing with 100% test pass rate. |

---

## 4. Design System — Light Magenta Palette

The platform features a clean, high-contrast **Light Magenta** design system:

- **Primary Action Accent (`#d946ef` / `#c026d3`)**: Used for primary action buttons (`.rim-btn-primary`), focal CTAs, and active navigation indicators.
- **Light Magenta Mist Wash (`#fdf4ff` / `#fae8ff`)**: Tinted background for announcement pills, highlighted table rows, and selected cards.
- **Hairline Accent Border (`#f0abfc`)**: Clean 1px accent dividers.
- **Typography**: Solid Black (`#000000`) and Deep Charcoal (`#1e293b`) for maximum enterprise contrast.
- **Surfaces**: Paper White (`#ffffff`) and Soft Stone (`#f8fafc`). *Zero cream, tan, or blue tones.*

---

## 5. Quick Start & Execution

### Prerequisites
- **Node.js**: v18.0.0 or higher
- **Python**: v3.10.0 or higher

### 1. Install Dependencies
```bash
# Frontend dependencies
npm install

# Backend dependencies
pip install -r backend/requirements.txt
```

### 2. Launch Backend Server
```bash
npm run backend
# Server runs on: http://127.0.0.1:8000
# Interactive API Docs: http://127.0.0.1:8000/docs
```

### 3. Launch Frontend Development Server
```bash
npm run dev
# Vite runs on: http://localhost:5173
```

### 4. Run Automated End-to-End Tests
```bash
npm run test:ui
# Runs 5 Playwright E2E test suites with 100% pass guarantee
```

### 5. Build for Production
```bash
npm run build
# Compiles production bundle into /dist
```

---

## 6. Key Documentation Links

- **Backend Architecture & System Specs**: [`docs/BACKEND_ARCHITECTURE.md`](docs/BACKEND_ARCHITECTURE.md)
- **Design System Guidelines**: [`docs/DESIGN.md`](docs/DESIGN.md)
- **Enterprise Full-Stack Implementation Plan**: [`docs/ENTERPRISE_FULLSTACK_PLAN.md`](docs/ENTERPRISE_FULLSTACK_PLAN.md)
- **Kaggle Dataset Integration Guide**: [`docs/KAGGLE_DATASET_INTEGRATION.md`](docs/KAGGLE_DATASET_INTEGRATION.md)
- **Complete Application Page Map**: [`docs/RIMBERIO_PAGE_DETAILS.md`](docs/RIMBERIO_PAGE_DETAILS.md)
- **Academic Research Materials**: [`material/`](material/)
