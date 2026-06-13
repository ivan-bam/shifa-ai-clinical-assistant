from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes import (
    clinical,
    documents,
    health,
    interactions,
    llm,
    soap,
    suggestions,
)
from backend.observability.logging_config import configure_logging, get_logger
from backend.observability.middleware import RequestLoggingMiddleware
from backend.services.db_init import init_database

configure_logging()
logger = get_logger("shifa.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the app starts: make sure the DB schema is in place.
    logger.info("Starting up — initialising database schema")
    init_database()
    logger.info("Startup complete")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Shifa AI Clinical Documentation Assistant",
    description="AI-assisted clinical documentation for Emergency Department physicians.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(health.router)
app.include_router(llm.router)
app.include_router(soap.router)
app.include_router(suggestions.router)
app.include_router(clinical.router)
app.include_router(interactions.router)
app.include_router(documents.router)
