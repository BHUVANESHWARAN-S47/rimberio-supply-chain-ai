import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import Column, DateTime, String, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase

class GUID(TypeDecorator):
    """Platform-independent GUID/UUID type.
    Uses PostgreSQL's native UUID type, otherwise uses CHAR(36) on SQLite.
    """
    impl = CHAR(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value) if isinstance(value, uuid.UUID) else value
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(str(value)))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(str(value))
            return value

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass

class TimestampMixin:
    """Standard timestamp mixin with timezone-aware defaults."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class ProvenanceMixin:
    """Data provenance tracking mixin ensuring data traceability."""
    data_source = Column(String(50), default="SYSTEM_GENERATED", nullable=False)
    # Allowed: PUBLIC_DATASET, SYNTHETIC, USER_CREATED, SYSTEM_GENERATED, SYSTEM_SCENARIO, IMPORTED_CSV, IMPORTED_EXCEL
    source_reference = Column(String(255), nullable=True)
