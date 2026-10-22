from typing import Optional
from datetime import datetime
from backend.app.cnt.models import BaselineState, CandidateAgreement
from backend.app.cnt.state_builder import StateBuilder


class BaselineManager:
    """Manages creation, serialization, and reproducibility of baseline states."""

    def __init__(self, state_builder: Optional[StateBuilder] = None):
        self.state_builder = state_builder or StateBuilder()

    def create_baseline(
        self,
        product_id: str,
        supplier_id: Optional[str] = None,
        order_quantity: Optional[int] = None,
        decision_timestamp: Optional[datetime] = None,
    ) -> BaselineState:
        """Constructs an auditable, reproducible baseline snapshot."""
        return self.state_builder.build_state(
            product_id=product_id,
            supplier_id=supplier_id,
            order_quantity=order_quantity,
            decision_timestamp=decision_timestamp,
        )

    def baseline_to_candidate_agreement(self, baseline: BaselineState) -> CandidateAgreement:
        """Converts the incumbent baseline state into a candidate agreement for direct comparison."""
        return CandidateAgreement(
            supplier_id=baseline.supplier_id,
            supplier_code=baseline.supplier_code,
            company_name=baseline.supplier_name,
            proposed_unit_price=baseline.current_unit_price,
            proposed_quantity=baseline.current_quantity,
            proposed_lead_time_days=baseline.current_lead_time_days,
            proposed_quality_score=round((1.0 - baseline.supplier_historical_defect_rate) * 100.0, 1),
            proposed_capacity=baseline.supplier_capacity,
            payment_terms="Net 30",
            transport_cost=round(baseline.current_quantity * 1.5, 2),
            is_incumbent=True,
        )
