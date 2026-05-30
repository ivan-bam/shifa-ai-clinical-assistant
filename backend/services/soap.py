from pydantic import BaseModel, Field

from backend.prompts.soap import SOAP_PROMPT_VERSION, SOAP_SYSTEM_PROMPT
from backend.services.llm import get_llm


class SOAPNote(BaseModel):
    subjective: str = Field(description="Patient-reported symptoms, history of presenting complaint.")
    objective: str = Field(description="Measured findings, vital signs, examination, investigations.")
    assessment: str = Field(description="Clinical impression and differential considerations.")
    plan: str = Field(description="Next steps: investigations, monitoring, treatment, disposition.")


class SOAPGenerationResult(BaseModel):
    note: SOAPNote
    model: str
    prompt_version: str
    ai_generated: bool = True


def generate_soap_note(physician_input: str, context: str = "") -> SOAPGenerationResult:
    llm = get_llm()
    structured_llm = llm.with_structured_output(SOAPNote)

    messages = [("system", SOAP_SYSTEM_PROMPT)]
    if context:
        messages.append((
            "system",
            f"Relevant clinical reference material retrieved from the knowledge base:\n\n{context}",
        ))
    messages.append(("user", physician_input))

    note: SOAPNote = structured_llm.invoke(messages)

    return SOAPGenerationResult(
        note=note,
        model=llm.model_name,
        prompt_version=SOAP_PROMPT_VERSION,
    )
