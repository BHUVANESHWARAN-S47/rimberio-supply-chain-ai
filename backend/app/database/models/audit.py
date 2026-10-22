import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Float, Integer, ForeignKey, Index, DateTime, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database.base import Base, GUID

class AgentExecutionDB(Base):
    __tablename__ = "agent_executions"
    __table_args__ = (
        Index("idx_agent_exec_session", "session_id"),
        Index("idx_agent_exec_name", "agent_name"),
        Index("idx_agent_exec_time", "created_at"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    status = Column(String(50), default="SUCCESS", nullable=False) # SUCCESS, ERROR, RETRY, TIMEOUT
    execution_time_ms = Column(Float, nullable=False)
    error = Column(Text, nullable=True)
    model_name = Column(String(100), default="DETERMINISTIC_ENGINE", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class AgentMessageDB(Base):
    __tablename__ = "agent_messages"
    __table_args__ = (
        Index("idx_agent_msg_session", "session_id"),
        Index("idx_agent_msg_agent", "agent_name"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)
    message_type = Column(String(50), nullable=False) # PROPOSAL, REASONING, ALERT, COUNTEROFFER
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class AuditLogDB(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_entity", "entity_type", "entity_id"),
        Index("idx_audit_time", "timestamp"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False) # CREATE, UPDATE, DELETE, OVERRIDE, EXPORT
    entity_type = Column(String(100), nullable=False) # supplier, rfq, quotation, decision
    entity_id = Column(String(100), nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(50), nullable=True)

    user = relationship("UserDB")

class SystemEventDB(Base):
    __tablename__ = "system_events"
    __table_args__ = (
        Index("idx_sys_event_type", "event_type"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(GUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False)
    severity = Column(String(50), default="INFO", nullable=False) # INFO, WARNING, ERROR, CRITICAL
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class KaggleStagingDB(Base):
    __tablename__ = "kaggle_staging"
    __table_args__ = (
        Index("idx_staging_batch", "import_batch_id"),
        Index("idx_staging_status", "status"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    import_batch_id = Column(String(100), nullable=False)
    dataset_name = Column(String(150), nullable=False)
    row_index = Column(Integer, nullable=False)
    raw_payload = Column(JSON, nullable=False)
    status = Column(String(50), default="PENDING", nullable=False) # PENDING, PROCESSED, ERROR, SKIPPED
    error_log = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
