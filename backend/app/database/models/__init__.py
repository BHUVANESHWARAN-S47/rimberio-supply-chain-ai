from backend.app.database.base import Base, GUID, TimestampMixin, ProvenanceMixin

from backend.app.database.models.master import (
    OrganizationDB, DepartmentDB, PermissionDB, RoleDB, RolePermissionDB,
    UserDB, UserRoleDB, AIAgentDB, AICapabilityDB, RoleAICapabilityDB,
    SupplierDB, ProductDB, SupplierProductDB, CustomerDB, WarehouseDB, CarrierDB
)
from backend.app.database.models.procurement import (
    RFQDB, RFQItemDB, QuotationDB, QuotationItemDB,
    PurchaseOrderDB, PurchaseOrderItemDB
)
from backend.app.database.models.negotiation import (
    NegotiationDB, NegotiationRoundDB, NegotiationMessageDB
)
from backend.app.database.models.performance import (
    SupplierPerformanceDB, SupplierEvaluationDB, SupplierRiskScoreDB
)
from backend.app.database.models.inventory import (
    InventoryDB, InventoryMovementDB, InventorySnapshotDB
)
from backend.app.database.models.demand import (
    DemandHistoryDB, DemandForecastDB
)
from backend.app.database.models.logistics import (
    ShipmentDB, ShipmentEventDB, LogisticsEvaluationDB
)
from backend.app.database.models.quality import (
    QualityInspectionDB, QualityIncidentDB
)
from backend.app.database.models.risk import (
    RiskEventDB, RiskAssessmentDB
)
from backend.app.database.models.simulation import (
    SimulationRunDB, SimulationScenarioDB, SimulationResultDB
)
from backend.app.database.models.decision import (
    SupplierComparisonDB, AdaptiveDecisionDB
)
from backend.app.database.models.customer import (
    CustomerOrderDB, CustomerOrderItemDB, CustomerImpactDB, CustomerNotificationDB,
    SupportTicketDB
)
from backend.app.database.models.feedback import (
    PredictionActualDB, ModelFeedbackDB
)
from backend.app.database.models.audit import (
    AgentExecutionDB, AgentMessageDB, AuditLogDB, SystemEventDB, KaggleStagingDB
)

__all__ = [
    "Base", "GUID", "TimestampMixin", "ProvenanceMixin",
    # Enterprise Structure & RBAC
    "OrganizationDB", "DepartmentDB", "PermissionDB", "RoleDB", "RolePermissionDB",
    "UserDB", "UserRoleDB", "AIAgentDB", "AICapabilityDB", "RoleAICapabilityDB",
    # Master
    "SupplierDB", "ProductDB", "SupplierProductDB",
    "CustomerDB", "WarehouseDB", "CarrierDB",
    # Procurement
    "RFQDB", "RFQItemDB", "QuotationDB", "QuotationItemDB",
    "PurchaseOrderDB", "PurchaseOrderItemDB",
    # Negotiation
    "NegotiationDB", "NegotiationRoundDB", "NegotiationMessageDB",
    # Performance
    "SupplierPerformanceDB", "SupplierEvaluationDB", "SupplierRiskScoreDB",
    # Inventory
    "InventoryDB", "InventoryMovementDB", "InventorySnapshotDB",
    # Demand
    "DemandHistoryDB", "DemandForecastDB",
    # Logistics
    "ShipmentDB", "ShipmentEventDB", "LogisticsEvaluationDB",
    # Quality
    "QualityInspectionDB", "QualityIncidentDB",
    # Risk
    "RiskEventDB", "RiskAssessmentDB",
    # Simulation
    "SimulationRunDB", "SimulationScenarioDB", "SimulationResultDB",
    # Decision
    "SupplierComparisonDB", "AdaptiveDecisionDB",
    # Customer
    "CustomerOrderDB", "CustomerOrderItemDB", "CustomerImpactDB", "CustomerNotificationDB", "SupportTicketDB",
    # Feedback
    "PredictionActualDB", "ModelFeedbackDB",
    # Audit
    "AgentExecutionDB", "AgentMessageDB", "AuditLogDB", "SystemEventDB", "KaggleStagingDB"
]
