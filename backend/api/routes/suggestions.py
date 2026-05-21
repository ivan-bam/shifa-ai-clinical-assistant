from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.suggestions import (
    SuggestionsGenerationResult,
    generate_clinical_suggestions,
)

router = APIRouter()


class SuggestionsRequest(BaseModel):
    physician_input: str


@router.post("/suggestions/generate", response_model=SuggestionsGenerationResult)
def create_suggestions(request: SuggestionsRequest):
    return generate_clinical_suggestions(request.physician_input)
