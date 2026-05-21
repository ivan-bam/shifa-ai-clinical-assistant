from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.soap import SOAPGenerationResult, generate_soap_note

router = APIRouter()


class SOAPRequest(BaseModel):
    physician_input: str


@router.post("/soap/generate", response_model=SOAPGenerationResult)
def create_soap_note(request: SOAPRequest):
    return generate_soap_note(request.physician_input)
