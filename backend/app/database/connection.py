import os
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.app.core.config import settings

# Primary URLs from settings / env
SYNC_DB_URL = os.getenv(
    "DATABASE_SYNC_URL",
    os.getenv("DATABASE_URL", settings.DATABASE_URL)
)

# Normalize async / sync URLs
if SYNC_DB_URL.startswith("postgresql+asyncpg://"):
    SYNC_DB_URL = SYNC_DB_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
elif SYNC_DB_URL.startswith("sqlite+aiosqlite:///"):
    SYNC_DB_URL = SYNC_DB_URL.replace("sqlite+aiosqlite:///", "sqlite:///")

ASYNC_DB_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)
if ASYNC_DB_URL.startswith("postgresql://"):
    ASYNC_DB_URL = ASYNC_DB_URL.replace("postgresql://", "postgresql+asyncpg://")
elif ASYNC_DB_URL.startswith("sqlite:///"):
    ASYNC_DB_URL = ASYNC_DB_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

# Sync Engine
sync_connect_args = {"check_same_thread": False} if "sqlite" in SYNC_DB_URL else {}
sync_engine = create_engine(
    SYNC_DB_URL,
    connect_args=sync_connect_args,
    echo=False,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Async Engine
async_connect_args = {"check_same_thread": False} if "sqlite" in ASYNC_DB_URL else {}
try:
    async_engine = create_async_engine(
        ASYNC_DB_URL,
        connect_args=async_connect_args,
        echo=False,
        pool_pre_ping=True
    )
    AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
except Exception:
    async_engine = None
    AsyncSessionLocal = None

def get_db() -> Generator[Session, None, None]:
    """Dependency for synchronous database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for asynchronous database sessions."""
    if AsyncSessionLocal is None:
        raise RuntimeError("Async database engine is not configured.")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def check_db_connection() -> dict:
    """Verifies database connectivity and returns metadata."""
    try:
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            dialect = sync_engine.dialect.name
            return {
                "status": "CONNECTED" if result == 1 else "UNEXPECTED_RESULT",
                "dialect": dialect,
                "url": sync_engine.url.render_as_string(hide_password=True),
                "is_healthy": True
            }
    except Exception as e:
        return {
            "status": "DISCONNECTED",
            "error": str(e),
            "is_healthy": False
        }
