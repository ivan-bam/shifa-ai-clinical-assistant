from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from backend.services.soap import SOAPGenerationResult, generate_soap_note
from backend.services.suggestions import (
    SuggestionsGenerationResult,
    generate_clinical_suggestions,
)

WORKFLOW_VERSION = "clinical-workflow-v1"


class ClinicalWorkflowState(TypedDict):
    physician_input: str
    soap_result: SOAPGenerationResult | None
    suggestions_result: SuggestionsGenerationResult | None


class ClinicalWorkflowOutput(BaseModel):
    soap: SOAPGenerationResult
    suggestions: SuggestionsGenerationResult
    workflow_version: str
    ai_generated: bool = True


def _soap_node(state: ClinicalWorkflowState) -> dict:
    result = generate_soap_note(state["physician_input"])
    return {"soap_result": result}


def _suggestions_node(state: ClinicalWorkflowState) -> dict:
    result = generate_clinical_suggestions(state["physician_input"])
    return {"suggestions_result": result}


def _build_workflow():
    graph = StateGraph(ClinicalWorkflowState)
    graph.add_node("soap_generation", _soap_node)
    graph.add_node("suggestions_generation", _suggestions_node)
    graph.add_edge(START, "soap_generation")
    graph.add_edge("soap_generation", "suggestions_generation")
    graph.add_edge("suggestions_generation", END)
    return graph.compile()


_workflow = _build_workflow()


def run_clinical_workflow(physician_input: str) -> ClinicalWorkflowOutput:
    final_state: ClinicalWorkflowState = _workflow.invoke(
        {
            "physician_input": physician_input,
            "soap_result": None,
            "suggestions_result": None,
        }
    )

    return ClinicalWorkflowOutput(
        soap=final_state["soap_result"],
        suggestions=final_state["suggestions_result"],
        workflow_version=WORKFLOW_VERSION,
    )
