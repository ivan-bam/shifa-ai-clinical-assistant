from pydantic import BaseModel, Field

from backend.prompts.suggestions import (
    SUGGESTIONS_PROMPT_VERSION,
    SUGGESTIONS_SYSTEM_PROMPT,
)
from backend.services.llm import get_llm


class Diagnosis(BaseModel):
    name: str = Field(description="The diagnosis or differential being considered.")
    rationale: str = Field(description="Brief clinical reasoning for this diagnosis.")
    likelihood: str = Field(description="One of: high, moderate, low.")


class Investigation(BaseModel):
    name: str = Field(description="The investigation, test, or procedure to consider.")
    rationale: str = Field(description="Why this investigation is being suggested.")


class Medication(BaseModel):
    name: str = Field(description="Drug name.")
    dose: str = Field(description="Dose, route, and frequency in standard clinical format.")
    rationale: str = Field(description="Indication for this medication.")


class ScheduleItem(BaseModel):
    timeframe: str = Field(description="When this action should happen, e.g. 'Immediate', 'Within 1 hour'.")
    action: str = Field(description="The action, intervention, or reassessment to perform.")


class ClinicalSuggestions(BaseModel):
    diagnoses: list[Diagnosis]
    investigations: list[Investigation]
    medications: list[Medication]
    care_schedule: list[ScheduleItem]


class SuggestionsGenerationResult(BaseModel):
    suggestions: ClinicalSuggestions
    model: str
    prompt_version: str
    ai_generated: bool = True


def generate_clinical_suggestions(physician_input: str) -> SuggestionsGenerationResult:
    llm = get_llm()
    structured_llm = llm.with_structured_output(ClinicalSuggestions)

    suggestions: ClinicalSuggestions = structured_llm.invoke(
        [
            ("system", SUGGESTIONS_SYSTEM_PROMPT),
            ("user", physician_input),
        ]
    )

    return SuggestionsGenerationResult(
        suggestions=suggestions,
        model=llm.model_name,
        prompt_version=SUGGESTIONS_PROMPT_VERSION,
    )
