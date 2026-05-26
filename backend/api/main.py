from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes import clinical, health, interactions, llm, soap, suggestions
from backend.services.db_init import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the app starts: make sure the DB schema is in place.
    init_database()
    yield


app = FastAPI(
    title="Shifa AI Clinical Documentation Assistant",
    description="AI-assisted clinical documentation for Emergency Department physicians.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(llm.router)
app.include_router(soap.router)
app.include_router(suggestions.router)
app.include_router(clinical.router)
app.include_router(interactions.router)
