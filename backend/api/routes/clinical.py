import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.graphs.clinical_workflow import (
    ClinicalWorkflowOutput,
    run_clinical_workflow,
)
from backend.models.ai_interaction import AIInteraction
from backend.services.database import get_db

router = APIRouter()


class ClinicalWorkflowRequest(BaseModel):
    physician_input: str
    encounter_id: uuid.UUID | None = None
    physician_id: uuid.UUID | None = None


class ClinicalWorkflowResponse(BaseModel):
    interaction_id: uuid.UUID
    output: ClinicalWorkflowOutput


@router.post("/clinical/generate", response_model=ClinicalWorkflowResponse)
def run_full_workflow(
    request: ClinicalWorkflowRequest,
    db: Session = Depends(get_db),
):
    output = run_clinical_workflow(request.physician_input)

    interaction = AIInteraction(
        encounter_id=request.encounter_id,
        physician_id=request.physician_id,
        input_text=request.physician_input,
        generated_output=output.model_dump(mode="json"),
        model_used=output.soap.model,
        prompt_version=output.workflow_version,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    return ClinicalWorkflowResponse(interaction_id=interaction.id, output=output)
