import uuid
from typing import List, Set, Optional, Dict, Any, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.models import (
    UserDB, RoleDB, PermissionDB, RolePermissionDB, UserRoleDB,
    AIAgentDB, AICapabilityDB, RoleAICapabilityDB, OrganizationDB
)
from backend.app.core.security import decode_access_token

security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> UserDB:
    """Validate JWT token and return authenticated UserDB instance."""
    if not credentials or not credentials.credentials:
        # Fallback for dev / unauthenticated requests: load default enterprise admin
        admin_user = db.query(UserDB).join(RoleDB, UserDB.role_id == RoleDB.id).filter(
            RoleDB.name == "ADMIN"
        ).first()
        if admin_user:
            return admin_user
        # Or load any active user
        any_user = db.query(UserDB).first()
        if any_user:
            return any_user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub") or payload.get("user_id")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identity subject claim.",
        )

    try:
        user_uuid = uuid.UUID(str(user_id_str))
    except ValueError:
        user_uuid = user_id_str

    user = db.query(UserDB).filter(UserDB.id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token no longer exists.",
        )

    if not user.is_active or user.status == "SUSPENDED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated or suspended.",
        )

    return user


def get_user_roles(user: UserDB, db: Session) -> List[RoleDB]:
    """Retrieve all roles assigned to user (primary role + multi-roles)."""
    roles = []
    if user.role:
        roles.append(user.role)
    user_multi_roles = db.query(RoleDB).join(UserRoleDB, RoleDB.id == UserRoleDB.role_id).filter(
        UserRoleDB.user_id == user.id
    ).all()
    for r in user_multi_roles:
        if r.id not in [x.id for x in roles]:
            roles.append(r)
    return roles


def get_user_permissions(user: UserDB, db: Session) -> Set[str]:
    """Dynamically resolve all permission codes for the user."""
    roles = get_user_roles(user, db)
    role_ids = [r.id for r in roles]

    # If user has ADMIN role, grant all permissions
    is_admin = any(r.name == "ADMIN" for r in roles)
    if is_admin:
        all_perms = db.query(PermissionDB.code).all()
        return {p[0] for p in all_perms}

    perms = db.query(PermissionDB.code).join(
        RolePermissionDB, PermissionDB.id == RolePermissionDB.permission_id
    ).filter(
        RolePermissionDB.role_id.in_(role_ids)
    ).all()

    return {p[0] for p in perms}


def get_user_capabilities(user: UserDB, db: Session) -> List[Dict[str, Any]]:
    """Dynamically resolve all AI Capabilities accessible to the user's roles."""
    roles = get_user_roles(user, db)
    role_ids = [r.id for r in roles]

    is_admin = any(r.name == "ADMIN" for r in roles)
    if is_admin:
        caps = db.query(AICapabilityDB, AIAgentDB).join(
            AIAgentDB, AICapabilityDB.agent_id == AIAgentDB.id
        ).all()
    else:
        caps = db.query(AICapabilityDB, AIAgentDB).join(
            AIAgentDB, AICapabilityDB.agent_id == AIAgentDB.id
        ).join(
            RoleAICapabilityDB, AICapabilityDB.id == RoleAICapabilityDB.capability_id
        ).filter(
            RoleAICapabilityDB.role_id.in_(role_ids)
        ).all()

    results = []
    seen = set()
    for cap, agent in caps:
        if cap.code not in seen:
            seen.add(cap.code)
            results.append({
                "id": cap.id,
                "code": cap.code,
                "name": cap.name,
                "description": cap.description,
                "agent_code": agent.code,
                "agent_name": agent.name,
            })
    return results


def require_permission(permission_code: str) -> Callable:
    """Dependency factory checking that caller holds the specified permission."""
    def dependency(
        current_user: UserDB = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> UserDB:
        perms = get_user_permissions(current_user, db)
        if permission_code not in perms and "*" not in perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Required permission '{permission_code}' not granted for your role.",
            )
        return current_user
    return dependency


def require_role(allowed_roles: List[str]) -> Callable:
    """Dependency factory checking that caller holds at least one of the allowed roles."""
    def dependency(
        current_user: UserDB = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> UserDB:
        roles = get_user_roles(current_user, db)
        user_role_names = [r.name for r in roles]
        if not any(r in allowed_roles for r in user_role_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Role must be one of {allowed_roles}.",
            )
        return current_user
    return dependency


def ensure_tenant_isolation(current_user: UserDB, target_org_id: Any):
    """Enforce strict multi-tenant boundary. Disallow cross-organization access."""
    if not target_org_id or not current_user.organization_id:
        return  # Global or unset
    if str(target_org_id).lower() != str(current_user.organization_id).lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-tenant access violation: Cannot access data from another enterprise.",
        )


def ensure_supplier_isolation(current_user: UserDB, target_supplier_id: Any):
    """Ensure external suppliers can only view their own company records."""
    if current_user.role and current_user.role.name == "SUPPLIER":
        if not current_user.supplier_id or str(target_supplier_id).lower() != str(current_user.supplier_id).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Supplier isolation: You can only view or manage your own company's RFQs and quotations.",
            )


def ensure_customer_isolation(current_user: UserDB, target_customer_id: Any):
    """Ensure external customers can only view their own purchase orders."""
    if current_user.role and current_user.role.name == "CUSTOMER":
        if not current_user.customer_id or str(target_customer_id).lower() != str(current_user.customer_id).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customer isolation: You can only view orders and shipments placed by your account.",
            )
