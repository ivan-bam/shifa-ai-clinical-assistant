from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.embedded_document import EmbeddedDocument
from backend.services.embeddings import embed_text, embed_texts

CHUNK_SIZE = 800       # characters per chunk
CHUNK_OVERLAP = 100    # characters of overlap between chunks


def _split_into_chunks(content: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_text(content)


def add_document(
    db: Session,
    source_type: str,
    source_id: str,
    content: str,
) -> list[EmbeddedDocument]:
    """Split content into chunks, embed each chunk, and persist them."""
    chunks = _split_into_chunks(content)
    vectors = embed_texts(chunks)

    records = [
        EmbeddedDocument(
            source_type=source_type,
            source_id=source_id,
            content=chunk,
            embedding=vector,
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    db.add_all(records)
    db.commit()
    for record in records:
        db.refresh(record)
    return records


def search_documents(
    db: Session,
    query: str,
    top_k: int = 5,
) -> list[EmbeddedDocument]:
    """Find the top_k chunks most semantically similar to the query."""
    query_vector = embed_text(query)
    stmt = (
        select(EmbeddedDocument)
        .order_by(EmbeddedDocument.embedding.cosine_distance(query_vector))
        .limit(top_k)
    )
    return list(db.execute(stmt).scalars().all())
