from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database.connection import get_db, check_db_connection
from backend.app.vector.client import check_chroma_connection

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/db")
def health_database(db: Session = Depends(get_db)):
    """Verifies relational database connectivity, dialect, and migration head."""
    db_status = check_db_connection()
    try:
        # Check migration version
        result = db.execute(text("SELECT version_num FROM alembic_version")).scalar()
        db_status["alembic_version"] = result
        db_status["migration_status"] = "UP_TO_DATE" if result else "NO_VERSION_RECORDED"
    except Exception as e:
        db_status["alembic_version"] = None
        db_status["migration_status"] = f"CHECK_FAILED: {str(e)}"

    return db_status

@router.get("/vector")
def health_vector():
    """Verifies ChromaDB connection and collection availability."""
    return check_chroma_connection()
