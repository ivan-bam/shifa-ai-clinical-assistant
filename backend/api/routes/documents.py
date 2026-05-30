import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.rag.service import add_document, search_documents
from backend.services.database import get_db

router = APIRouter()


class DocumentCreateRequest(BaseModel):
    source_type: str   # e.g. "guideline", "drug_info", "protocol"
    source_id: str     # e.g. "WHO-ED-Chest-Pain-2024"
    content: str


class DocumentChunkRead(BaseModel):
    id: uuid.UUID
    source_type: str
    source_id: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentCreateResponse(BaseModel):
    chunks_created: int
    source_type: str
    source_id: str


@router.post("/documents", response_model=DocumentCreateResponse)
def upload_document(request: DocumentCreateRequest, db: Session = Depends(get_db)):
    records = add_document(
        db=db,
        source_type=request.source_type,
        source_id=request.source_id,
        content=request.content,
    )
    return DocumentCreateResponse(
        chunks_created=len(records),
        source_type=request.source_type,
        source_id=request.source_id,
    )


@router.get("/documents/search", response_model=list[DocumentChunkRead])
def search(query: str, top_k: int = 5, db: Session = Depends(get_db)):
    return search_documents(db=db, query=query, top_k=top_k)
