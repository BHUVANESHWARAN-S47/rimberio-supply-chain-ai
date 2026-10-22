from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.database.models import (
    SupplierDB, SupplierPerformanceDB, NegotiationDB, NegotiationRoundDB,
    AdaptiveDecisionDB, SimulationRunDB, SimulationScenarioDB, SimulationResultDB
)
from backend.app.vector.collections import get_collection, init_chroma_collections
from backend.app.vector.embeddings import generate_embedding

class ChromaSyncService:
    """Synchronizes authoritative PostgreSQL structured state into ChromaDB semantic collections.
    Enforces unidirectional synchronization: PostgreSQL -> ChromaDB.
    """

    def __init__(self, db: Session):
        self.db = db
        init_chroma_collections()

    def sync_suppliers(self) -> int:
        col = get_collection("rimberio_supplier_memory")
        suppliers = self.db.query(SupplierDB).all()
        synced = 0

        for s in suppliers:
            # Query recent performance
            perfs = self.db.query(SupplierPerformanceDB).filter(SupplierPerformanceDB.supplier_id == s.id).all()
            avg_quality = sum(p.quality_score for p in perfs) / len(perfs) if perfs else 92.0
            ontime_pct = (sum(1 for p in perfs if p.on_time) / len(perfs) * 100.0) if perfs else 95.0

            doc_text = (
                f"Supplier Profile: {s.company_name} ({s.supplier_code}). Location: {s.city}, {s.country}. "
                f"Status: {s.status}, Type: {s.supplier_type}, Payment Terms: {s.payment_terms}. "
                f"Historical Reliability: {ontime_pct:.1f}% on-time delivery rate, "
                f"Quality index: {avg_quality:.1f} points based on {len(perfs)} historical orders."
            )
            emb = generate_embedding(doc_text)
            col.upsert(
                ids=[f"sup_{s.id}"],
                documents=[doc_text],
                embeddings=[emb],
                metadatas=[{
                    "supplier_id": str(s.id),
                    "supplier_code": s.supplier_code,
                    "company_name": s.company_name,
                    "country": s.country,
                    "source": "postgresql_sync"
                }]
            )
            synced += 1
        return synced

    def sync_negotiations(self) -> int:
        col = get_collection("rimberio_negotiation_memory")
        negotiations = self.db.query(NegotiationDB).all()
        synced = 0

        for n in negotiations:
            rounds = self.db.query(NegotiationRoundDB).filter(NegotiationRoundDB.negotiation_id == n.id).order_by(NegotiationRoundDB.round_number.asc()).all()
            final_round = rounds[-1] if rounds else None
            final_price = final_round.offered_price if final_round else 0.0

            doc_text = (
                f"Historical Negotiation: Session with Supplier ID {n.supplier_id}. "
                f"Status: {n.status}. Total rounds executed: {len(rounds)}. "
                f"Final settlement/offer price: ${final_price:.2f}. "
                f"Concession details: {final_round.proposal if final_round else 'N/A'}."
            )
            emb = generate_embedding(doc_text)
            col.upsert(
                ids=[f"neg_{n.id}"],
                documents=[doc_text],
                embeddings=[emb],
                metadatas=[{
                    "negotiation_id": str(n.id),
                    "supplier_id": str(n.supplier_id),
                    "status": n.status,
                    "rounds_count": len(rounds),
                    "source": "postgresql_sync"
                }]
            )
            synced += 1
        return synced

    def sync_decisions(self) -> int:
        col = get_collection("rimberio_decision_memory")
        decisions = self.db.query(AdaptiveDecisionDB).all()
        synced = 0

        for d in decisions:
            doc_text = (
                f"Adaptive Decision Record: Action {d.decision_type} selected for Simulation Run {d.simulation_run_id}. "
                f"Selected Supplier ID: {d.selected_supplier_id} with confidence {d.confidence * 100:.1f}%. "
                f"Executive Reasoning: {d.reasoning}"
            )
            emb = generate_embedding(doc_text)
            col.upsert(
                ids=[f"dec_{d.id}"],
                documents=[doc_text],
                embeddings=[emb],
                metadatas=[{
                    "decision_id": str(d.id),
                    "simulation_run_id": str(d.simulation_run_id),
                    "decision_type": d.decision_type,
                    "confidence": float(d.confidence),
                    "source": "postgresql_sync"
                }]
            )
            synced += 1
        return synced

    def sync_simulations(self) -> int:
        col = get_collection("rimberio_simulation_memory")
        scenarios = self.db.query(SimulationScenarioDB).all()
        synced = 0

        for sc in scenarios:
            res_list = self.db.query(SimulationResultDB).filter(SimulationResultDB.simulation_scenario_id == sc.id).all()
            for r in res_list:
                doc_text = (
                    f"Counterfactual Scenario: {sc.scenario_type} - {sc.description}. "
                    f"Candidate Supplier {r.candidate_supplier_id}: Quote ${r.candidate_price:.2f}, "
                    f"Delivery {r.candidate_delivery_days} days. Predicted Cost: ${r.predicted_cost:.2f}, "
                    f"Predicted Delivery Delay: {r.predicted_delivery_delay} days, "
                    f"Predicted Stockout Rate: {r.predicted_stockout_rate * 100:.1f}%, "
                    f"Service Level: {r.predicted_service_level:.1f}%."
                )
                emb = generate_embedding(doc_text)
                col.upsert(
                    ids=[f"sim_{r.id}"],
                    documents=[doc_text],
                    embeddings=[emb],
                    metadatas=[{
                        "scenario_id": str(sc.id),
                        "result_id": str(r.id),
                        "scenario_type": sc.scenario_type,
                        "candidate_supplier_id": str(r.candidate_supplier_id),
                        "source": "postgresql_sync"
                    }]
                )
                synced += 1
        return synced

    def sync_all(self) -> Dict[str, int]:
        """Runs the entire PostgreSQL -> ChromaDB synchronization suite."""
        return {
            "suppliers_synced": self.sync_suppliers(),
            "negotiations_synced": self.sync_negotiations(),
            "decisions_synced": self.sync_decisions(),
            "simulations_synced": self.sync_simulations(),
        }
