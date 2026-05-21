from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from backend.services.llm import get_llm

router = APIRouter()


class LLMRequest(BaseModel):
    prompt: str


class LLMResponse(BaseModel):
    response: str
    model: str


@router.post("/llm/test", response_model=LLMResponse)
def test_llm(request: LLMRequest):
    llm = get_llm()
    result = llm.invoke([HumanMessage(content=request.prompt)])
    return LLMResponse(response=result.content, model=llm.model_name)
