from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import (
    customization,
    agents,
    simulation,
    suppliers,
    decision,
    customer_impact,
    learning,
    data_router,
)

from backend.database.seed_db import init_db

app = FastAPI(
    title="RIMBERIO AI Supply Chain Twin — Backend API",
    description="Enterprise API powering autonomous multi-agent negotiation, counterfactual simulations, adaptive switching, and full system customization.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
def on_startup():
    init_db()

# Enable CORS for React/Vite development & production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(customization.router)
app.include_router(agents.router)
app.include_router(simulation.router)
app.include_router(suppliers.router)
app.include_router(decision.router)
app.include_router(customer_impact.router)
app.include_router(learning.router)
app.include_router(data_router.router)

@app.get("/")
def root():
    return {
        "platform": "RIMBERIO AI Digital Twin",
        "status": "ONLINE",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "customization": "/api/customization/profile",
            "agents": "/api/agents/negotiate/session/SES-AUTONOMOUS-01",
            "simulation": "/api/simulation/counterfactual",
            "suppliers": "/api/suppliers",
            "decision": "/api/decision/evaluate",
            "customer_impact": "/api/customer-impact/orders",
            "learning": "/api/learning/metrics"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "HEALTHY", "service": "rimberio-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
