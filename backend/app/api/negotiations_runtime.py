"""Authenticated adapter between the legacy negotiation engine and enterprise tables."""
from typing import Any, Dict
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.auth import get_current_user, get_user_roles
from backend.app.database.connection import get_db
from backend.app.database.models import NegotiationDB, NegotiationRoundDB, NegotiationMessageDB, SupplierDB, UserDB
from backend.models.schemas import NegotiationStepRequest
from backend.services.agents_engine import agents_engine

router = APIRouter(prefix="/api/v1/negotiations/runtime", tags=["Negotiation Runtime"])
ALLOWED_ROLES = {"ADMIN", "PROCUREMENT_MANAGER", "BUYER", "SUPPLIER"}


def negotiation_user(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserDB:
    roles = {role.name for role in get_user_roles(current_user, db)}
    if not roles.intersection(ALLOWED_ROLES):
        raise HTTPException(status_code=403, detail="Negotiation access is not permitted for this role.")
    return current_user


def _persist_session(session: Any, user: UserDB, db: Session) -> None:
    supplier = db.query(SupplierDB).filter(SupplierDB.supplier_code == session.supplier_code).first()
    if not supplier:
        # If not found by supplier_code, try to find first or skip DB persistence
        supplier = db.query(SupplierDB).first()
    if not supplier:
        return

    record = (
        db.query(NegotiationDB)
        .filter(
            NegotiationDB.organization_id == user.organization_id,
            NegotiationDB.buyer_id == user.id,
            NegotiationDB.supplier_id == supplier.id,
            NegotiationDB.status.notin_(["APPROVED", "REJECTED"]),
        )
        .order_by(NegotiationDB.created_at.desc())
        .first()
    )
    if record is None:
        record = NegotiationDB(
            id=uuid.uuid4(),
            organization_id=user.organization_id,
            supplier_id=supplier.id,
            buyer_id=user.id,
            status=session.status,
            current_round=session.current_round,
        )
        db.add(record)
        db.flush()
    else:
        record.status = session.status
        record.current_round = session.current_round

    existing_rounds = {
        (round_record.round_number, round_record.actor_type)
        for round_record in record.rounds
    }
    for bid in session.history:
        actor_type = bid.role if bid.role in {"BUYER", "SUPPLIER", "SYSTEM"} else "SYSTEM"
        key = (bid.round, actor_type)
        if key in existing_rounds:
            continue
        round_record = NegotiationRoundDB(
            negotiation_id=record.id,
            round_number=bid.round,
            actor_type=actor_type,
            actor_id=bid.agent_id,
            offered_price=bid.proposed_price,
            quantity=14820,
            delivery_days=bid.proposed_lead_time_days,
            proposal=bid.message,
            accepted=bid.status == "AGREED",
        )
        db.add(round_record)
        db.flush()
        db.add(NegotiationMessageDB(
            negotiation_id=record.id,
            round_id=round_record.id,
            sender_type=actor_type,
            message=bid.message,
            structured_offer={
                "price": bid.proposed_price,
                "delivery_days": bid.proposed_lead_time_days,
                "status": bid.status,
            },
        ))
    db.commit()


class NegotiationStartPayload(NegotiationStepRequest.__base__):
    supplier_code: str
    supplier_name: str = ""
    sku_code: str
    target_price: float = 140.0


@router.post("/start")
def start_runtime_session(
    payload: NegotiationStartPayload,
    user: UserDB = Depends(negotiation_user),
    db: Session = Depends(get_db),
):
    session = agents_engine.start_session(
        supplier_code=payload.supplier_code,
        supplier_name=payload.supplier_name or payload.supplier_code,
        sku_code=payload.sku_code,
    )
    if payload.target_price:
        session.buyer_target = float(payload.target_price)
    _persist_session(session, user, db)
    return session


@router.get("/{session_id}")
def get_runtime_session(
    session_id: str,
    user: UserDB = Depends(negotiation_user),
):
    session = agents_engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Negotiation session not found.")
    return session


@router.post("/step")
def execute_runtime_step(
    payload: NegotiationStepRequest,
    user: UserDB = Depends(negotiation_user),
    db: Session = Depends(get_db),
):
    session = agents_engine.execute_step(payload)
    _persist_session(session, user, db)
    return session

