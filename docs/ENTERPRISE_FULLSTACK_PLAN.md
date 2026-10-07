# RIMBERIO Enterprise Full-Stack Implementation Plan
> **Architectural Blueprint: Production Database, ML Models, Agentic AI, and Light Magenta Design System**

---

## 1. Architectural Phases

### Phase 1: Design System & Color Palette Transformation (Light Magenta)
- **Objective**: Purge all cream, tan, blue, and teal colors across the entire frontend.
- **Color Tokens**:
  - Primary Action Magenta: `#d946ef` / `#c026d3`
  - Light Magenta Mist Wash: `#fdf4ff` / `#fae8ff`
  - Subtle Magenta Border / Accent: `#f0abfc`
  - Surfaces: `#ffffff` (Paper White), `#f8fafc` / `#fdf4ff` (Cards)
  - Typography: Solid Black (`#000000`) and Deep Charcoal (`#1e293b`) for maximum enterprise contrast.
- **Components to Update**: `src/index.css`, `Header.jsx`, `Sidebar.jsx`, `LandingPage.jsx`, `DashboardPage.jsx`, `SimulationPage.jsx`, `NegotiationPage.jsx`, `SupplierPage.jsx`, `DecisionCenterPage.jsx`, `CustomerImpactPage.jsx`, `LearningFeedbackPage.jsx`, `LoginPage.jsx`, `RegisterPage.jsx`.

### Phase 2: Relational Database Persistence (SQLAlchemy & SQLite)
- **Objective**: Replace ephemeral in-memory storage with a real relational database (`sqlite:///./backend/data/rimberio_enterprise.db`).
- **Tables**:
  - `SuppliersTable`
  - `CustomerOrdersTable`
  - `NegotiationSessionsTable` & `NegotiationBidsTable`
  - `SimulationExperimentsTable`
  - `FulfillmentTelemetryTable`
  - `CustomizationProfilesTable`
- **Initial Data**: Seeded from authentic Kaggle DataCo & Supply Chain Analysis datasets.

### Phase 3: Machine Learning & Agentic AI Models
- **Objective**: Implement enterprise-grade mathematical and ML models for the 5 agents:
  1. **Buyer Agent**: Procurement optimization model with multi-attribute utility and Boulware concession curve.
  2. **Supplier Agent**: Cost margin model with production volume discounts and capacity limits.
  3. **Logistics Agent**: Maritime/freight transit variance model with chokepoint queueing delays.
  4. **Customer Impact Agent**: SLA penalty contract calculator and customer churn risk model.
  5. **Admin Auditor Agent**: Real Scikit-learn Classifier (Random Forest) for Retain/Negotiate/Switch policy with dynamic confusion matrix.
  6. **Counterfactual Negotiation Twin (CNT)**: Causal Monte Carlo simulation engine with 1,000+ stochastic trials.

### Phase 4: Frontend-Backend Live API Client Integration
- **Objective**: Connect React pages to live FastAPI endpoints via a centralized `src/services/api.js` client:
  - Live Suppliers table (`/api/suppliers`)
  - Live Counterfactual simulation (`/api/simulation/counterfactual`)
  - Live Autonomous negotiation runner (`/api/agents/negotiate/step`)
  - Live Customer orders & automated notice dispatch (`/api/customer-impact/orders`)
  - Live Confusion matrix and model recalibration (`/api/learning/metrics`)
  - Live Kaggle dataset overview (`/api/data/kaggle/summary`)

### Phase 5: Verification, Testing & Quality Assurance
- Run Playwright test suite (`npx playwright test`).
- Verify production build (`npm run build`).
- Verify live backend endpoints (`http://127.0.0.1:8000/docs`).
