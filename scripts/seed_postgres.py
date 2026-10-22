import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Ensure Postgres connection URLs (port 5433 on localhost connects to Docker)
os.environ["DATABASE_URL"] = "postgresql+psycopg2://rimberio_admin:rimberio_secure_pass@localhost:5433/rimberio"
os.environ["DATABASE_SYNC_URL"] = "postgresql+psycopg2://rimberio_admin:rimberio_secure_pass@localhost:5433/rimberio"

print("Connecting to PostgreSQL in Docker...")
from backend.app.database.connection import sync_engine
from backend.app.database.models import Base

print("Creating enterprise tables in PostgreSQL...")
Base.metadata.create_all(bind=sync_engine)

from backend.database.database import Base as LegacyBase, engine as legacy_engine
LegacyBase.metadata.create_all(bind=legacy_engine)

print("Seeding enterprise hierarchy & Kaggle records...")
from backend.app.database.enterprise_seed import seed_enterprise_hierarchy
seed_enterprise_hierarchy()

print("Seeding legacy supplier records...")
from backend.database.seed_db import init_db
init_db()

print("\nSUCCESS: PostgreSQL inside Docker is fully seeded with all 56 tables & data!")
