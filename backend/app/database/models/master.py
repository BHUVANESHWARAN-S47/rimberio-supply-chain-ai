import uuid
from sqlalchemy import (
    Column, String, Text, Float, Integer, Boolean, ForeignKey, 
    UniqueConstraint, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base, GUID, TimestampMixin, ProvenanceMixin

# ============================================================================
# 1. ENTERPRISE TENANT & HIERARCHY MODELS
# ============================================================================

class OrganizationDB(Base, TimestampMixin):
    """Enterprise Tenant. Provides strict multi-tenant isolation."""
    __tablename__ = "organizations"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    industry = Column(String(100), nullable=False, default="Manufacturing", index=True)
    country = Column(String(100), nullable=False, default="Global")
    location = Column(String(200), nullable=True)
    contact_email = Column(String(150), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    settings_json = Column(Text, nullable=True)  # Industry-specific & tenant configuration
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    departments = relationship("DepartmentDB", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("UserDB", back_populates="organization", cascade="all, delete-orphan")
    roles = relationship("RoleDB", back_populates="organization", cascade="all, delete-orphan")


class DepartmentDB(Base, TimestampMixin):
    """Configurable enterprise departments (Procurement, Supply Chain, Logistics, etc.)."""
    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_org_dept_code"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    head_user_id = Column(GUID, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    organization = relationship("OrganizationDB", back_populates="departments")
    users = relationship("UserDB", back_populates="department")


# ============================================================================
# 2. RBAC & PERMISSION MODELS
# ============================================================================

class PermissionDB(Base):
    """Granular platform action permission (e.g. rfq.create, cnt.run)."""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False, index=True)  # PROCUREMENT, LOGISTICS, ADMIN, etc.
    description = Column(String(255), nullable=True)

    role_permissions = relationship("RolePermissionDB", back_populates="permission", cascade="all, delete-orphan")


class RoleDB(Base):
    """Enterprise Human Role (ADMIN, PROCUREMENT_MANAGER, BUYER, custom roles)."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(50), nullable=False, index=True)
    display_name = Column(String(100), nullable=True)
    description = Column(String(255), nullable=True)
    is_system = Column(Boolean, default=True, nullable=False)  # True for built-in, False for custom

    # Relationships
    organization = relationship("OrganizationDB", back_populates="roles")
    users = relationship("UserDB", back_populates="role", foreign_keys="UserDB.role_id")
    role_permissions = relationship("RolePermissionDB", back_populates="role", cascade="all, delete-orphan")
    role_capabilities = relationship("RoleAICapabilityDB", back_populates="role", cascade="all, delete-orphan")


class RolePermissionDB(Base):
    """Join table linking Roles to Permissions."""
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True)

    role = relationship("RoleDB", back_populates="role_permissions")
    permission = relationship("PermissionDB", back_populates="role_permissions")


# ============================================================================
# 3. AI AGENT REGISTRY & CAPABILITY MODELS
# ============================================================================

class AIAgentDB(Base):
    """Platform AI Agent service metadata."""
    __tablename__ = "ai_agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    service_class = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    capabilities = relationship("AICapabilityDB", back_populates="agent", cascade="all, delete-orphan")


class AICapabilityDB(Base):
    """AI Capability exposed to user roles (e.g. Procurement Intelligence, What-If)."""
    __tablename__ = "ai_capabilities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    agent_id = Column(Integer, ForeignKey("ai_agents.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(String(255), nullable=True)

    agent = relationship("AIAgentDB", back_populates="capabilities")
    role_capabilities = relationship("RoleAICapabilityDB", back_populates="capability", cascade="all, delete-orphan")


class RoleAICapabilityDB(Base):
    """Join table linking Roles to AI Capabilities."""
    __tablename__ = "role_ai_capabilities"
    __table_args__ = (
        UniqueConstraint("role_id", "capability_id", name="uq_role_capability"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    capability_id = Column(Integer, ForeignKey("ai_capabilities.id", ondelete="CASCADE"), nullable=False, index=True)

    role = relationship("RoleDB", back_populates="role_capabilities")
    capability = relationship("AICapabilityDB", back_populates="role_capabilities")


# ============================================================================
# 4. USER MODEL (HUMAN & EXTERNAL STAKEHOLDER)
# ============================================================================

class UserDB(Base, TimestampMixin):
    """Human user or external stakeholder belonging to an organization & department."""
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    department_id = Column(GUID, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    supplier_id = Column(GUID, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, index=True)
    customer_id = Column(GUID, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=True)
    location = Column(String(150), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    status = Column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, INVITED, SUSPENDED
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    organization = relationship("OrganizationDB", back_populates="users")
    department = relationship("DepartmentDB", back_populates="users")
    role = relationship("RoleDB", back_populates="users", foreign_keys=[role_id])
    supplier = relationship("SupplierDB", foreign_keys=[supplier_id])
    customer = relationship("CustomerDB", foreign_keys=[customer_id])
    
    user_roles = relationship("UserRoleDB", back_populates="user", cascade="all, delete-orphan")
    rfqs = relationship("RFQDB", back_populates="buyer", foreign_keys="RFQDB.buyer_id")
    purchase_orders = relationship("PurchaseOrderDB", back_populates="buyer", foreign_keys="PurchaseOrderDB.buyer_id")


class UserRoleDB(Base):
    """Multi-role assignment for users."""
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("UserDB", back_populates="user_roles")
    role = relationship("RoleDB")


# ============================================================================
# 5. ENTERPRISE BUSINESS & MASTER ENTITIES
# ============================================================================

class SupplierDB(Base, TimestampMixin, ProvenanceMixin):
    __tablename__ = "suppliers"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    supplier_code = Column(String(50), unique=True, nullable=False, index=True)
    company_name = Column(String(200), nullable=False, index=True)
    contact_name = Column(String(150), nullable=True)
    email = Column(String(150), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False, default="Global")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(50), default="ACTIVE", nullable=False, index=True)
    supplier_type = Column(String(50), default="STANDARD", nullable=False)
    payment_terms = Column(String(50), default="Net 30", nullable=False)

    products = relationship("SupplierProductDB", back_populates="supplier", cascade="all, delete-orphan")
    quotations = relationship("QuotationDB", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrderDB", back_populates="supplier")
    performances = relationship("SupplierPerformanceDB", back_populates="supplier")
    risk_events = relationship("RiskEventDB", back_populates="supplier")
    risk_assessments = relationship("RiskAssessmentDB", back_populates="supplier")


class ProductDB(Base, TimestampMixin, ProvenanceMixin):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("unit_cost >= 0", name="check_product_unit_cost_positive"),
        CheckConstraint("selling_price >= 0", name="check_product_selling_price_positive"),
        CheckConstraint("safety_stock >= 0", name="check_product_safety_stock_positive"),
        CheckConstraint("reorder_point >= 0", name="check_product_reorder_point_positive"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    unit = Column(String(50), default="unit", nullable=False)
    unit_weight = Column(Float, default=1.0, nullable=False)
    unit_cost = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    lead_time_days = Column(Integer, default=14, nullable=False)
    safety_stock = Column(Integer, default=500, nullable=False)
    reorder_point = Column(Integer, default=1000, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    suppliers = relationship("SupplierProductDB", back_populates="product", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryDB", back_populates="product")
    rfq_items = relationship("RFQItemDB", back_populates="product")


class SupplierProductDB(Base, TimestampMixin):
    __tablename__ = "supplier_products"
    __table_args__ = (
        UniqueConstraint("supplier_id", "product_id", name="uq_supplier_product"),
        CheckConstraint("unit_price >= 0", name="check_supplier_unit_price_positive"),
        CheckConstraint("minimum_order_quantity >= 1", name="check_supplier_moq_positive"),
        CheckConstraint("lead_time_days >= 1", name="check_supplier_lead_time_positive"),
        CheckConstraint("quality_rating >= 0 AND quality_rating <= 100", name="check_supplier_quality_bounds"),
        Index("idx_sup_prod_supplier", "supplier_id"),
        Index("idx_sup_prod_product", "product_id"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    supplier_id = Column(GUID, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(GUID, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    supplier_sku = Column(String(100), nullable=True)
    unit_price = Column(Float, nullable=False)
    minimum_order_quantity = Column(Integer, default=100, nullable=False)
    lead_time_days = Column(Integer, default=14, nullable=False)
    capacity = Column(Integer, default=50000, nullable=False)
    quality_rating = Column(Float, default=90.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    supplier = relationship("SupplierDB", back_populates="products")
    product = relationship("ProductDB", back_populates="suppliers")


class CustomerDB(Base, TimestampMixin, ProvenanceMixin):
    __tablename__ = "customers"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    customer_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    email = Column(String(150), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="Global", nullable=False)
    customer_type = Column(String(50), default="COMMERCIAL", nullable=False)
    priority = Column(String(50), default="STANDARD", nullable=False)

    orders = relationship("CustomerOrderDB", back_populates="customer")
    impacts = relationship("CustomerImpactDB", back_populates="customer")
    notifications = relationship("CustomerNotificationDB", back_populates="customer")


class WarehouseDB(Base, TimestampMixin):
    __tablename__ = "warehouses"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    warehouse_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    location = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="Global", nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    capacity = Column(Integer, default=100000, nullable=False)

    inventory_items = relationship("InventoryDB", back_populates="warehouse")


class CarrierDB(Base, TimestampMixin):
    __tablename__ = "carriers"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    carrier_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    service_type = Column(String(50), default="STANDARD_FREIGHT", nullable=False)
    average_transit_days = Column(Float, default=5.0, nullable=False)
    reliability_score = Column(Float, default=95.0, nullable=False)

    shipments = relationship("ShipmentDB", back_populates="carrier")
