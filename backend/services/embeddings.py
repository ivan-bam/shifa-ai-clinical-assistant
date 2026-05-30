from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()  # ensure .env is loaded regardless of import order

EMBEDDING_MODEL = "text-embedding-3-small"


@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    """Return a cached OpenAIEmbeddings client."""
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)


def embed_text(text: str) -> list[float]:
    """Embed a single string into a 1536-dimension vector."""
    return get_embeddings().embed_query(text)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of strings into vectors (more efficient than one at a time)."""
    return get_embeddings().embed_documents(texts)
