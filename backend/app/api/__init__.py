from backend.app.api.health import router as health_router
from backend.app.api.crud_routes import router as crud_router
from backend.app.api.cnt import router as cnt_router
from backend.app.api.agents import router as agents_router
from backend.app.api.auth import router as auth_router
from backend.app.api.me import router as me_router
from backend.app.api.admin import router as admin_router

__all__ = [
    "health_router", "crud_router", "cnt_router", "agents_router",
    "auth_router", "me_router", "admin_router",
]
