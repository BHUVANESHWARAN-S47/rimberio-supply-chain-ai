from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from backend.app.database.repositories.base_repository import BaseRepository
from backend.app.database.models.simulation import (
    SimulationRunDB, SimulationScenarioDB, SimulationResultDB
)
from backend.app.database.models.decision import (
    AdaptiveDecisionDB, SupplierComparisonDB
)

class SimulationRunRepository(BaseRepository[SimulationRunDB]):
    def __init__(self, db: Session):
        super().__init__(SimulationRunDB, db)

    def get_by_run_id(self, run_id: str) -> Optional[SimulationRunDB]:
        return (
            self.db.query(SimulationRunDB)
            .options(
                joinedload(SimulationRunDB.scenarios).joinedload(SimulationScenarioDB.results),
                joinedload(SimulationRunDB.decision),
                joinedload(SimulationRunDB.comparisons)
            )
            .filter(SimulationRunDB.run_id == run_id)
            .first()
        )

class AdaptiveDecisionRepository(BaseRepository[AdaptiveDecisionDB]):
    def __init__(self, db: Session):
        super().__init__(AdaptiveDecisionDB, db)

    def get_by_run_id(self, simulation_run_id) -> Optional[AdaptiveDecisionDB]:
        return self.db.query(AdaptiveDecisionDB).filter(AdaptiveDecisionDB.simulation_run_id == simulation_run_id).first()

class SupplierComparisonRepository(BaseRepository[SupplierComparisonDB]):
    def __init__(self, db: Session):
        super().__init__(SupplierComparisonDB, db)

    def get_rankings(self, simulation_run_id) -> List[SupplierComparisonDB]:
        return (
            self.db.query(SupplierComparisonDB)
            .filter(SupplierComparisonDB.simulation_run_id == simulation_run_id)
            .order_by(SupplierComparisonDB.rank.asc())
            .all()
        )
