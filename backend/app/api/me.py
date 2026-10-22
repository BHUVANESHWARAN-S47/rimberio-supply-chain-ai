"""
RIMBERIO Enterprise — User Context Endpoints (/me)
===================================================
GET /api/v1/me               — Current user profile
GET /api/v1/me/permissions    — Resolved permission codes
GET /api/v1/me/capabilities   — Resolved AI capabilities
GET /api/v1/me/navigation     — Role-aware navigation items
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import UserDB
from backend.app.core.auth import (
    get_current_user, get_user_roles, get_user_permissions, get_user_capabilities
)

router = APIRouter(prefix="/api/v1/me", tags=["User Context"])


# ── Role → Navigation Mapping ──
# This is the ONLY place navigation is configured.
# It is NOT hardcoded in the frontend — the frontend fetches this from /me/navigation.

ROLE_NAVIGATION = {
    "ADMIN": [
        {"id": "dashboard", "label": "Admin Home", "icon": "LayoutDashboard", "section": "HOME"},
        {"id": "admin_users", "label": "Users & Roles", "icon": "Users", "section": "ADMINISTRATION"},
        {"id": "admin_departments", "label": "Departments", "icon": "Building2", "section": "ADMINISTRATION"},
        {"id": "suppliers", "label": "Suppliers", "icon": "Search", "section": "SUPPLY CHAIN"},
        {"id": "products", "label": "Products", "icon": "Package", "section": "SUPPLY CHAIN"},
        {"id": "warehouses_carriers", "label": "Warehouses & Carriers", "icon": "Truck", "section": "SUPPLY CHAIN"},
        {"id": "ai_agents", "label": "AI Agents", "icon": "Brain", "section": "AI & SYSTEM"},
        {"id": "ai_health", "label": "AI Health", "icon": "Activity", "section": "AI & SYSTEM"},
        {"id": "audit_logs", "label": "Activity History", "icon": "FileText", "section": "GOVERNANCE"},
    ],
    "BUYER": [
        {"id": "dashboard", "label": "Buying Home", "icon": "LayoutDashboard", "section": "HOME"},
        {"id": "find_suppliers", "label": "Find Suppliers", "icon": "Search", "section": "BUYING"},
        {"id": "my_products", "label": "My Products", "icon": "Package", "section": "BUYING"},
        {"id": "rfqs", "label": "Price Requests", "icon": "FileText", "section": "BUYING"},
        {"id": "negotiations", "label": "Price Talks", "icon": "MessageSquare", "section": "BUYING"},
        {"id": "what_if", "label": "What-If Check", "icon": "Sliders", "section": "BUYING"},
        {"id": "purchase_orders", "label": "Purchase Orders", "icon": "ShoppingCart", "section": "BUYING"},
    ],
    "PROCUREMENT_MANAGER": [
        {"id": "dashboard", "label": "Buying Home", "icon": "LayoutDashboard", "section": "HOME"},
        {"id": "find_suppliers", "label": "Find Suppliers", "icon": "Search", "section": "BUYING"},
        {"id": "my_products", "label": "My Products", "icon": "Package", "section": "BUYING"},
        {"id": "rfqs", "label": "Price Requests", "icon": "FileText", "section": "BUYING"},
        {"id": "negotiations", "label": "Price Talks", "icon": "MessageSquare", "section": "BUYING"},
        {"id": "what_if", "label": "What-If Check", "icon": "Sliders", "section": "BUYING"},
        {"id": "purchase_orders", "label": "Purchase Orders", "icon": "ShoppingCart", "section": "BUYING"},
    ],
    "LOGISTICS_MANAGER": [
        {"id": "dashboard", "label": "Shipping Home", "icon": "LayoutDashboard", "section": "HOME"},
        {"id": "shipments", "label": "Shipments", "icon": "Truck", "section": "SHIPPING"},
        {"id": "carriers", "label": "Carriers", "icon": "Ship", "section": "SHIPPING"},
        {"id": "warehouses", "label": "Warehouses", "icon": "Building", "section": "SHIPPING"},
        {"id": "stock", "label": "Stock", "icon": "Package", "section": "SHIPPING"},
        {"id": "delays", "label": "Delays & Routes", "icon": "Clock", "section": "SHIPPING"},
    ],
    "SUPPLY_CHAIN_ANALYST": [
        {"id": "dashboard", "label": "Shipping Home", "icon": "LayoutDashboard", "section": "HOME"},
        {"id": "shipments", "label": "Shipments", "icon": "Truck", "section": "SHIPPING"},
        {"id": "carriers", "label": "Carriers", "icon": "Ship", "section": "SHIPPING"},
        {"id": "warehouses", "label": "Warehouses", "icon": "Building", "section": "SHIPPING"},
        {"id": "stock", "label": "Stock", "icon": "Package", "section": "SHIPPING"},
        {"id": "delays", "label": "Delays & Routes", "icon": "Clock", "section": "SHIPPING"},
    ],
    "SUPPLIER": [
        {"id": "dashboard", "label": "Supplier Home", "icon": "LayoutDashboard", "section": "HOME"},
        {"id": "my_company", "label": "My Company", "icon": "Building", "section": "PORTAL"},
        {"id": "my_products", "label": "My Products", "icon": "Package", "section": "PORTAL"},
        {"id": "rfqs", "label": "Price Requests & Quotes", "icon": "FileText", "section": "PORTAL"},
        {"id": "negotiations", "label": "Price Talks", "icon": "MessageSquare", "section": "PORTAL"},
        {"id": "orders_to_deliver", "label": "Orders To Deliver", "icon": "ShoppingCart", "section": "PORTAL"},
    ],
    "CUSTOMER": [
        {"id": "dashboard", "label": "My Orders Home", "icon": "LayoutDashboard", "section": "HOME"},
        {"id": "my_orders", "label": "My Orders", "icon": "ShoppingBag", "section": "MY ACCOUNT"},
        {"id": "order_tracking", "label": "Order Tracking", "icon": "MapPin", "section": "MY ACCOUNT"},
        {"id": "notifications", "label": "Notifications", "icon": "Bell", "section": "MY ACCOUNT"},
        {"id": "support", "label": "Support", "icon": "HelpCircle", "section": "MY ACCOUNT"},
    ],
}


# Default fallback for custom roles
DEFAULT_NAVIGATION = [
    {"id": "dashboard", "label": "Dashboard", "icon": "LayoutDashboard", "section": "OVERVIEW"},
]


@router.get("")
def get_me(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return the authenticated user's full profile including organization, department, and role details."""
    roles = get_user_roles(current_user, db)
    role_names = [r.name for r in roles]
    role_displays = [r.display_name or r.name for r in roles]

    org_info = None
    if current_user.organization:
        org_info = {
            "id": str(current_user.organization.id),
            "name": current_user.organization.name,
            "industry": current_user.organization.industry,
            "country": current_user.organization.country,
        }

    dept_info = None
    if current_user.department:
        dept_info = {
            "id": str(current_user.department.id),
            "name": current_user.department.name,
            "code": current_user.department.code,
        }

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "location": current_user.location,
        "status": current_user.status,
        "role": role_names[0] if role_names else None,
        "role_display": role_displays[0] if role_displays else None,
        "roles": role_names,
        "organization": org_info,
        "department": dept_info,
        "avatar_url": f"https://ui-avatars.com/api/?name={current_user.full_name.replace(' ', '+')}&background=8e3a59&color=fff&bold=true&size=64",
    }


@router.get("/permissions")
def get_my_permissions(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return all resolved permission codes for the current user."""
    perms = get_user_permissions(current_user, db)
    return {
        "user_id": str(current_user.id),
        "permissions": sorted(list(perms)),
        "count": len(perms),
    }


@router.get("/capabilities")
def get_my_capabilities(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return all AI capabilities accessible to the current user based on their role."""
    caps = get_user_capabilities(current_user, db)
    return {
        "user_id": str(current_user.id),
        "capabilities": caps,
        "count": len(caps),
    }


@router.get("/navigation")
def get_my_navigation(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return role-aware navigation items for the current user's sidebar."""
    roles = get_user_roles(current_user, db)
    role_names = [r.name for r in roles]

    # Use the primary role's navigation
    primary_role = role_names[0] if role_names else None
    nav_items = ROLE_NAVIGATION.get(primary_role, DEFAULT_NAVIGATION)

    # Group by section
    sections: Dict[str, list] = {}
    for item in nav_items:
        section = item.get("section", "OTHER")
        if section not in sections:
            sections[section] = []
        sections[section].append({
            "id": item["id"],
            "label": item["label"],
            "icon": item["icon"],
        })

    return {
        "role": primary_role,
        "role_display": roles[0].display_name if roles else None,
        "items": nav_items,
        "sections": sections,
    }
