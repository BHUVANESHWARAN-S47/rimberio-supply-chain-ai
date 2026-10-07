# RIMBERIO AI SUPPLY CHAIN TWIN
## Complete Application Page Map & Content Documentation

---

- **Theme**: Earthy Ivory Light — `#A49A87` (Sand), `#A5A58D` (Sage), `#968F83` (Taupe), `#E8E5DF` (Cream)
- **Typography Color**: **Solid Black (`#000000`) entirely** across all headings, titles, labels, tables, and body text
- **Font Family**: Nunito 800 (Lemon Milk aesthetic) — Bold uppercase headers, letter-spacing
- **Navigation Flow**: Landing Page → Login / Register → Dashboard (+ enterprise workspace tools)

---

## PAGE MAP OVERVIEW

```
[1] Landing Page            ← Public entry point & platform showcase
    ├── Sign In             → [2] Login Page
    └── Get Started         → [3] Register Page
        └── Forgot Key      → [4] Forgot Password Page

[Authenticated Enterprise Workspace — 9-Step Research Pipeline]
[5] Dashboard Page          ← Real-time Intelligence Hub & Global Telemetry
[6] Negotiation Page        ← Step 3: Multi-Agent AI Autonomous Negotiation Console
[7] Simulation Page         ← Step 4: Counterfactual Negotiation Twin (CNT) "What-If" Sim
[8] Supplier Page           ← Steps 1 & 2: Supplier Data & Weighted Evaluation Workspace
[9] Decision Center Page    ← Steps 5 & 6: Adaptive Decision Module (Retain/Negotiate/Switch)
[10] Customer Impact Page   ← Steps 7 & 8: Customer Impact Analysis & Automated Notice Dispatch
[11] Learning Feedback Page ← Step 9: Predicted vs Actual Outcomes & Confusion Matrix
[12] Reports Page           ← System Audits & Technical Documentation

[Multi-Agent Roles Architecture (Section III-A & IV-A)]
- Role 1: Buyer Agent (Enterprise Procurement Lead)
- Role 2: Supplier Agent (Vendor Representative — Apex Global)
- Role 3: Logistics Agent (Global Freight & Port Telemetry)
- Role 4: Customer Impact Agent (Customer Relations & Notification Officer)
- Role 5: Operations Lead / Admin (System Auditor & Model Supervisor)
```

---

## PAGE DETAILS

---
### [1] LANDING PAGE
- **Route**: `currentPage = 'landing'`
- **File**: `src/pages/LandingPage.jsx`
- **Access**: Public — Default entry point

**Purpose**: High-impact enterprise presentation of the RIMBERIO AI Supply Chain Twin.

**Sections**:
- **Navigation Bar**: RIMBERIO brand mark, navigation anchors, Sign In and Get Started CTAs.
- **Hero Section**: Earthy gradient background, *"INTELLIGENT SUPPLY CHAIN OPERATIONS"* headline in crisp black, Live platform status badge, Launch and Sign-in buttons.
- **Stats Banner**: Key metrics: YTD Savings ($412,800), Active SKUs (14,820), SLA Compliance (99.4%), Telemetry Nodes (142).
- **Features Grid**: 6 enterprise capability cards: Autonomous AI Negotiation, Global Digital Twin, Adaptive Decision Engine, Supplier Risk Index, Predictive Analytics, and Enterprise Zero-Trust Security.
- **Enterprise Call-to-Action**: Direct conversion banner to provision new company workspaces.
- **Footer**: Copyright, quick links, and enterprise compliance badges.

---
### [2] LOGIN PAGE
- **Route**: `currentPage = 'login'`
- **File**: `src/pages/LoginPage.jsx`
- **Access**: Public

**Purpose**: Secure corporate gateway for authenticated supply chain managers and logistics operators.

**Sections**:
- **Left Brand Panel** (desktop): Earthy gradient, platform capabilities, SOC2 Type II, AES-256, and ISO 27001 badges.
- **Right Form Panel**: Solid black header *"ENTERPRISE SIGN IN"*, corporate email field, security key password field with show/hide toggle, "Forgot Key?" link, 30-day session retention checkbox, and *"Authenticate & Launch Platform"* CTA.
- **Demo Mode**: Pre-loaded with `elena.rostova@rimberio.ai`.

---
### [3] REGISTER PAGE
- **Route**: `currentPage = 'register'`
- **File**: `src/pages/RegisterPage.jsx`
- **Access**: Public

**Purpose**: New organization deployment and workspace provisioning.

**Sections**:
- **Left Brand Panel** (desktop): Enterprise deployment overview and included features.
- **Right Form Panel**: Full Name, Corporate Email, Organization Name, Role/Designation, Security Key creation, enterprise provisioning details, and *"Initialize Workspace & Launch"* CTA.

---
### [4] FORGOT PASSWORD PAGE
- **Route**: `currentPage = 'forgot_password'`
- **File**: `src/pages/ForgotPasswordPage.jsx`
- **Access**: Public

**Purpose**: Zero-trust security credential recovery.

**Sections**:
- **Header**: RIMBERIO branding with quick *"Back to Sign In"* navigation.
- **Credential Recovery Form**: Security Shield badge, email dispatch field, and instant validation confirmation.

---
### [5] DASHBOARD PAGE (Main Hub)
- **Route**: `currentPage = 'dashboard'`
- **File**: `src/pages/DashboardPage.jsx`
- **Access**: Authenticated

**Purpose**: Primary supply chain command center with real-time digital twin telemetry, global node status, and disruption alerts.

**Sections**:
- **Title Banner**: *"SUPPLY CHAIN INTELLIGENCE DASHBOARD"* with live UTC timestamp, shortcuts to Counterfactual Simulation and AI Negotiation.
- **Disruption Alert**: Critical Suez Canal disruption banner detailing impacted SKUs, cost estimates, delay days, and direct action to apply mitigation.
- **KPI Metrics (4 Cards)**: Total Active SKUs (14,820), Autonomous Negotiations (18 Rounds), YTD Savings Generated ($412,800), Global Network Latency (14.2 Days).
- **Global Network Map**: Interactive canvas featuring 5 international logistics hubs (Shanghai, Rotterdam, Los Angeles, Singapore, Hamburg) with live delay indicators, tooltips, and telemetry status.
- **Live AI Event Log**: Real-time event feed of autonomous price concessions, maritime reroutes, and buffer reconciliations.

---
### [6] AI NEGOTIATION CONSOLE
- **Route**: `currentPage = 'negotiation'`
- **File**: `src/pages/NegotiationPage.jsx`
- **Access**: Authenticated

**Purpose**: Live multi-agent negotiation interface where RIMBERIO's autonomous agent negotiates spot-market procurement contracts with suppliers.

**Sections**:
- **Console Banner**: Multi-Agent active status, vendor context (*Semiconductor Direct Corp*), agent pause/resume controls, and concession forcing.
- **Agreement Metrics Card**: Real-time target price vs. supplier offer, SLA lead time, and projected cost savings.
- **Parameter Controls**: Interactive sliders to adjust Target Unit Price ($) and Maximum Lead Time (Days).
- **Live Terminal**: Encrypted round-by-round chat feed between the RIMBERIO Buyer Agent and Supplier AI Agent, with manual directive injection.

---
### [7] COUNTERFACTUAL TWIN SIMULATION
- **Route**: `currentPage = 'simulation'`
- **File**: `src/pages/SimulationPage.jsx`
- **Access**: Authenticated

**Purpose**: Scenario playground allowing operators to test macroeconomic shocks against the supply chain twin before committing real-world actions.

**Sections**:
- **Scenario Banner**: *"PREDICTIVE PLAYGROUND"* with scenario tracking and mitigation shortcut.
- **Disruption Controls**: Maritime delay sliders, freight rate surge modifiers, regional demand surge, and Tier-1 supplier failure toggles.
- **Simulated Impact Projections**: Real-time calculated cost impact ($) and SLA risk breach probability (%).
- **Mitigation Recommendations**: Side-by-side trade-off analysis of Option A (Hamburg Rail Reroute) vs. Option B (Air Freight Expedite).

---
### [8] SUPPLIER INTELLIGENCE WORKSPACE
- **Route**: `currentPage = 'suppliers'`
- **File**: `src/pages/SupplierPage.jsx`
- **Access**: Authenticated

**Purpose**: Vendor directory and multi-criteria risk scoring.

**Sections**:
- **Workspace Banner**: 504 tracked vendors, ESG certification indicator, and at-risk vendor counters.
- **Filter Pills**: All, Healthy, Warning, Critical, Tier 1, Tier 2, Tier 3.
- **Supplier Scorecard Table**: Supplier Name, Tier, Geographic Region, Category, Real-time Status Badge, SLA Performance Bar, Risk Index (0-100), Average Delivery Time, YTD Spend, and ESG Rating.

---
### [9] ADAPTIVE DECISION CENTER
- **Route**: `currentPage = 'decision_center'`
- **File**: `src/pages/DecisionCenterPage.jsx`
- **Access**: Authenticated

**Purpose**: Autonomous mitigation playbook ranking solutions for active supply chain disruptions.

**Sections**:
- **Playbook Banner**: Model confidence rating (98.2%) and active disruption reference.
- **Decision Options**:
  - **Option A (Recommended)**: Hamburg Rail Reroute + Spot Negotiation (+$42K cost, saves $210K, 98.2% confidence).
  - **Option B**: Air Freight Frankfurt Expedite (+$190K cost, zero delay, 96.0% confidence).
  - **Option C**: Dual Supplier Failover Yokohama (+$78K cost, saves $140K, 88.7% confidence).
- **Execution Confirmation**: Interactive dispatch trigger with instant telemetry push.

---
### [10] CUSTOMER IMPACT & NOTIFICATION ENGINE (STEPS 7 & 8)
- **Route**: `currentPage = 'customer_impact'`
- **File**: `src/pages/CustomerImpactPage.jsx`
- **Access**: Authenticated

**Purpose**: Downstream transparency engine that calculates SLA impact for all affected client orders when switching suppliers, with automated transparency notice dispatch.

**Sections**:
- **Pipeline Eyebrow**: `PIPELINE STEPS 7 & 8` · `CUSTOMER-AWARE TWIN` badges.
- **Metric Cards**: Affected Accounts (5 Clients, 61,670 Units), Avg Transit Delta (+2.8 Days), SLA Adherence (98.6%), Notices Dispatched live counter.
- **Affected Orders Table**: Boeing, Tesla Energy, Siemens Healthineers, Foxconn, and ABB Robotics with revised ETAs, SLA risk classification, and individual "Send Notice" triggers.
- **Live Advisory Preview & Dispatcher**: Formatted client transparency memo with recipient, subject, reasons for supplier switching, revised guaranteed ETA, and 1-click batch dispatch.

---
### [11] PREDICTED VS ACTUAL PERFORMANCE & LEARNING LOOP (STEP 9)
- **Route**: `currentPage = 'learning_feedback'`
- **File**: `src/pages/LearningFeedbackPage.jsx`
- **Access**: Authenticated

**Purpose**: Validation and continuous reinforcement loop comparing Counterfactual Negotiation Twin simulations against actual post-switch logistics outcomes.

**Sections**:
- **Pipeline Eyebrow**: `PIPELINE STEP 9` · `FEEDBACK LOOP` badges.
- **Stats Banner**: Overall Accuracy (92.4%), Mean Absolute Error / MAE (0.34 Days), Root Mean Squared Error / RMSE (0.48 Days), Active Policy Version.
- **Fig. 1 Confusion Matrix**: Interactive 3x3 classification matrix for `RETAIN`, `NEGOTIATE`, and `SWITCH` decisions across 1,000 synthetic simulation episodes with Class Precision, Recall, and F1-Scores.
- **Counterfactual Prediction Error Table**: Section IV-D empirical delta tracking for Delivery Lead Time, Negotiated Unit Cost, Stockout Probability, Quality Defect Rate, and Carbon Footprint.
- **Interactive Policy Retraining**: One-click "Retrain Twin Policy" button that updates model weights and broadcasts a real-time system event.

---
### [12] REPORTS & PLATFORM ARCHITECTURE
- **Route**: `currentPage = 'reports'`
- **File**: `src/pages/ReportsPage.jsx`
- **Access**: Authenticated

**Purpose**: Document library providing downloadable audit logs, post-mortems, and technical architecture references.

**Sections**:
- **Library Table**: Document ID, Title, Category Badge (Quarterly, Disruption, Financial, ESG, Technical), Publication Date, Status, Page Count, and PDF Download action.

---

## GLOBAL NAVIGATION & COMPONENTS

### 1. Header (`src/components/Header.jsx`)
- **Visibility**: Rendered across all authenticated pages (hidden on Landing, Login, Register, Forgot Password).
- **Contents**:
  - RIMBERIO logo mark and version indicator (`v4.2`).
  - Real-time `AI AGENT AUTONOMOUS` operational indicator.
  - Disruption warning badge (`⚠ SUEZ DISRUPTION — CRITICAL MITIGATION`).
  - **Multi-Agent Role Switcher**: Interactive selector supporting all 5 project personas (Buyer, Supplier, Logistics, Customer Impact, Operations Lead).
  - System notifications bell.
  - User profile menu with enterprise designation and Sign Out action.
- *(Note: Unwanted ZIP download buttons and hub links have been removed for clean enterprise workflow).*

### 2. Sidebar (`src/components/Sidebar.jsx`)
- **Visibility**: Rendered across all authenticated pages.
- **Navigation Links**:
  1. `Intelligence Dashboard` (LIVE)
  2. `AI Negotiation Console` (AI)
  3. `Counterfactual Twin Sim` (SIM)
  4. `Supplier Workspace` (98%)
  5. `Adaptive Decision Center` (AUTO)
  6. `Customer Impact & Notices` (CLIENT)
  7. `Learning Loop & Confusion Mat` (LEARN)
  8. `Reports & Architecture`
- **Twin Node Status Widget**: Live active stream telemetry (14ms ping, 99.98% uptime).
- **Sign Out Button**: Quick secure session logout.
- *(Note: Auth screens have been removed from the sidebar so the navigation reflects real platform tools).*

---

## DESIGN SYSTEM TOKENS

| Token | Value | Applied Role |
| :--- | :--- | :--- |
| **All Typography** | `#000000` | **Solid Black font color entirely across the whole UI** |
| `--color-cream` | `#FDF4F9` | **Light Magenta Wash (Replaced Cream)** — Main page background surface |
| `--color-magenta` | `#C026D3` | **Magenta Accent** — Modern visual pop for pulse indicators and primary alerts |
| `--color-sage` / `--color-lavender` | `#CBC4D6` | **User Swatch (Lilac Mist)** — Alternative to olive green for badges, icon tiles, and highlights |
| `--color-sand` | `#8A8098` | Slate Lilac — secondary brand accents & border strokes |
| `--color-white` | `#FFFFFF` | Crisp Pure White — elevated card surfaces |
| `--color-light` | `#FCE7F3` | Soft Magenta Tint — input background & hover states |
| `--color-dark` | `#000000` | Primary text token |
| `--color-mid` | `#000000` | Secondary text token |

---
*Documentation updated: October 2026 — RIMBERIO AI Supply Chain Twin*
