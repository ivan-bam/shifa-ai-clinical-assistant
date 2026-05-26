import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.ai_interaction import AIInteraction
from backend.services.database import get_db

router = APIRouter()


class InteractionRead(BaseModel):
    id: uuid.UUID
    encounter_id: uuid.UUID | None
    physician_id: uuid.UUID | None
    input_text: str
    generated_output: dict[str, Any]
    approved_output: dict[str, Any] | None
    model_used: str
    prompt_version: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


@router.get("/interactions", response_model=list[InteractionRead])
def list_interactions(limit: int = 20, db: Session = Depends(get_db)):
    stmt = (
        select(AIInteraction)
        .order_by(AIInteraction.created_at.desc())
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


@router.get("/interactions/{interaction_id}", response_model=InteractionRead)
def get_interaction(interaction_id: uuid.UUID, db: Session = Depends(get_db)):
    interaction = db.get(AIInteraction, interaction_id)
    if interaction is None:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


class ApprovalRequest(BaseModel):
    approved_output: dict[str, Any]
    physician_id: uuid.UUID | None = None


@router.post("/interactions/{interaction_id}/approve", response_model=InteractionRead)
def approve_interaction(
    interaction_id: uuid.UUID,
    request: ApprovalRequest,
    db: Session = Depends(get_db),
):
    interaction = db.get(AIInteraction, interaction_id)
    if interaction is None:
        raise HTTPException(status_code=404, detail="Interaction not found")

    interaction.approved_output = request.approved_output
    if request.physician_id is not None:
        interaction.physician_id = request.physician_id

    db.commit()
    db.refresh(interaction)
    return interaction


@router.get("/interactions/pending/list", response_model=list[InteractionRead])
def list_pending_interactions(limit: int = 20, db: Session = Depends(get_db)):
    """Interactions that have not yet been reviewed by a physician."""
    stmt = (
        select(AIInteraction)
        .where(AIInteraction.approved_output.is_(None))
        .order_by(AIInteraction.created_at.desc())
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()
