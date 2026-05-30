from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.rag.service import search_documents
from backend.services.soap import SOAPGenerationResult, generate_soap_note
from backend.services.suggestions import (
    SuggestionsGenerationResult,
    generate_clinical_suggestions,
)

WORKFLOW_VERSION = "clinical-workflow-v2"
TOP_K = 5  # how many reference chunks to retrieve


class RetrievedChunk(BaseModel):
    source_type: str
    source_id: str
    content: str


class ClinicalWorkflowState(TypedDict):
    physician_input: str
    db: Any                          # SQLAlchemy Session — held in memory, never serialized
    retrieved_chunks: list[dict]     # serializable list of retrieved chunks (for the response)
    context: str                     # formatted text for the LLM
    soap_result: SOAPGenerationResult | None
    suggestions_result: SuggestionsGenerationResult | None


class ClinicalWorkflowOutput(BaseModel):
    soap: SOAPGenerationResult
    suggestions: SuggestionsGenerationResult
    retrieved_chunks: list[RetrievedChunk]
    workflow_version: str
    ai_generated: bool = True


def _retrieval_node(state: ClinicalWorkflowState) -> dict:
    docs = search_documents(
        db=state["db"],
        query=state["physician_input"],
        top_k=TOP_K,
    )
    if not docs:
        return {"retrieved_chunks": [], "context": ""}

    retrieved_chunks = [
        {
            "source_type": d.source_type,
            "source_id": d.source_id,
            "content": d.content,
        }
        for d in docs
    ]
    context = "\n\n".join(
        f"[Source: {d['source_id']} | Type: {d['source_type']}]\n{d['content']}"
        for d in retrieved_chunks
    )
    return {"retrieved_chunks": retrieved_chunks, "context": context}


def _soap_node(state: ClinicalWorkflowState) -> dict:
    result = generate_soap_note(state["physician_input"], context=state["context"])
    return {"soap_result": result}


def _suggestions_node(state: ClinicalWorkflowState) -> dict:
    result = generate_clinical_suggestions(state["physician_input"], context=state["context"])
    return {"suggestions_result": result}


def _build_workflow():
    graph = StateGraph(ClinicalWorkflowState)
    graph.add_node("retrieval", _retrieval_node)
    graph.add_node("soap_generation", _soap_node)
    graph.add_node("suggestions_generation", _suggestions_node)
    graph.add_edge(START, "retrieval")
    graph.add_edge("retrieval", "soap_generation")
    graph.add_edge("soap_generation", "suggestions_generation")
    graph.add_edge("suggestions_generation", END)
    return graph.compile()


_workflow = _build_workflow()


def run_clinical_workflow(physician_input: str, db: Session) -> ClinicalWorkflowOutput:
    final_state: ClinicalWorkflowState = _workflow.invoke(
        {
            "physician_input": physician_input,
            "db": db,
            "retrieved_chunks": [],
            "context": "",
            "soap_result": None,
            "suggestions_result": None,
        }
    )

    return ClinicalWorkflowOutput(
        soap=final_state["soap_result"],
        suggestions=final_state["suggestions_result"],
        retrieved_chunks=[RetrievedChunk(**c) for c in final_state["retrieved_chunks"]],
        workflow_version=WORKFLOW_VERSION,
    )
