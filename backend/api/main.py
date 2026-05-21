from fastapi import FastAPI

from backend.api.routes import health, llm, soap, suggestions

app = FastAPI(
    title="Shifa AI Clinical Documentation Assistant",
    description="AI-assisted clinical documentation for Emergency Department physicians.",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(llm.router)
app.include_router(soap.router)
app.include_router(suggestions.router)
