# RIMBERIO Backend Server

FastAPI backend powering the **RIMBERIO AI Supply Chain Twin** with full customization capabilities.

---

## Features

1. **Full Customization Control Plane (`/api/customization`)**:
   - Dynamic Criteria Weights (Cost, Quality, Delivery, Reliability, Geopolitical Risk).
   - Agent Negotiation Heuristics (Boulware Beta parameter, target & reservation prices, LLM prompt overrides).
   - Monte Carlo Simulation Parameters (sample sizes, perturbation distributions, confidence intervals).
   - Decision Policy Configuration (switch threshold delta, risk ceilings).
   - Customer Notification Templates (Jinja2-style variable interpolation).

2. **Autonomous Multi-Agent Negotiation Engine (`/api/agents`)**:
   - Buyer Agent, Supplier Agent, Logistics Agent, Customer Impact Agent, Operations Auditor.
   - Time-dependent Boulware and concession curve state machine.

3. **Counterfactual Negotiation Twin (`/api/simulation`)**:
   - Monte Carlo stochastic simulations.
   - Lead-time Poisson drift and freight cost escalation distributions.
   - Value-at-Risk (VaR) and SLA breach probabilities.

4. **Adaptive Decision Center (`/api/decision` & `/api/suppliers`)**:
   - Multi-Criteria Decision Analysis (MCDA).
   - Retain / Negotiate / Switch classification engine.

5. **Customer Impact & Notice Dispatch (`/api/customer-impact`)**:
   - Affected order lines tracking.
   - Automated batch email/SMS notice generation.

6. **Continuous Learning Feedback Loop (`/api/learning`)**:
   - Real-time MAE, RMSE, MAPE tracking.
   - Retain/Negotiate/Switch confusion matrix.
   - Online model recalibration.

---

## Quick Start

### 1. Run Backend Server
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Interactive Swagger UI
Open your browser to:
- Interactive API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Alternative ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
