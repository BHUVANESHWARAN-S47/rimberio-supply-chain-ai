"""
RIMBERIO Enterprise Supply Chain Platform — Application Entry Point
===================================================================
Registers all API routers, initializes enterprise database, and serves as
the FastAPI application factory.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Legacy routers (will be gradually migrated behind auth)
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

# Enterprise database initialization
from backend.app.database.connection import sync_engine
from backend.app.database.models import Base

app = FastAPI(
    title="RIMBERIO Enterprise Supply Chain Platform",
    description="Production-grade, multi-tenant enterprise supply chain operating platform with RBAC, AI Agent Registry, and Counterfactual Simulation.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
def on_startup():
    """Create all enterprise tables and seed RBAC hierarchy on startup."""
    # 1. Create all SQLAlchemy tables from the enterprise model set
    Base.metadata.create_all(bind=sync_engine)

    # 2. Also create legacy tables (dual-database period)
    from backend.database.database import Base as LegacyBase, engine as legacy_engine
    LegacyBase.metadata.create_all(bind=legacy_engine)

    # 3. Seed enterprise hierarchy (orgs, depts, roles, permissions, agents, users)
    try:
        from backend.app.database.enterprise_seed import seed_enterprise_hierarchy
        seed_enterprise_hierarchy()
    except Exception as e:
        print(f"[STARTUP] Enterprise seed warning: {e}")

    # 4. Seed legacy data if needed
    try:
        from backend.database.seed_db import init_db
        init_db()
    except Exception as e:
        print(f"[STARTUP] Legacy seed warning: {e}")


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ENTERPRISE API ROUTERS (v2 — authenticated) ──
from backend.app.api.auth import router as auth_router
from backend.app.api.me import router as me_router
from backend.app.api.admin import router as admin_router
from backend.app.api.health import router as health_router
from backend.app.api.crud_routes import router as crud_router
from backend.app.api.cnt import router as cnt_router
from backend.app.api.agents import router as enterprise_agents_router
from backend.app.api.negotiations_runtime import router as negotiations_runtime_router

app.include_router(auth_router)
app.include_router(me_router)
app.include_router(admin_router)
app.include_router(health_router)
app.include_router(crud_router)
app.include_router(cnt_router)
app.include_router(enterprise_agents_router)
app.include_router(negotiations_runtime_router)

# ── LEGACY ROUTERS (backward compatibility) ──
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
        "platform": "RIMBERIO Enterprise Supply Chain Platform",
        "status": "ONLINE",
        "version": "2.0.0",
        "docs": "/docs",
        "auth": {
            "login": "/api/v1/auth/login",
            "register": "/api/v1/auth/register",
        },
        "user_context": {
            "profile": "/api/v1/me",
            "permissions": "/api/v1/me/permissions",
            "capabilities": "/api/v1/me/capabilities",
            "navigation": "/api/v1/me/navigation",
        },
        "admin": {
            "users": "/api/v1/admin/users",
            "departments": "/api/v1/admin/departments",
            "roles": "/api/v1/admin/roles",
            "permissions": "/api/v1/admin/permissions",
            "ai_capabilities": "/api/v1/admin/ai-capabilities",
        },
    }


@app.get("/health")
def health_check():
    return {"status": "HEALTHY", "service": "rimberio-enterprise", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
