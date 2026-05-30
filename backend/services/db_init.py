from sqlalchemy import text

from backend.models.ai_interaction import AIInteraction  # noqa: F401 (registers the table)
from backend.models.embedded_document import EmbeddedDocument  # noqa: F401
from backend.models.base import Base
from backend.services.database import engine


def init_database() -> None:
    """Enable the pgvector extension and create all tables if they don't exist."""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
