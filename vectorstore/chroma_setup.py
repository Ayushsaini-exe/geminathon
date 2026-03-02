"""
ChromaDB vector store setup for the RAG Knowledge Engine.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import get_settings
from app.core.logging import logger

_client = None
_collection = None

COLLECTION_NAME = "agro_knowledge"


def get_chroma_client() -> chromadb.ClientAPI:
    """Return a persistent ChromaDB client (singleton)."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info(f"ChromaDB client initialized at {settings.CHROMA_PERSIST_DIR}")
    return _client


def get_collection() -> chromadb.Collection:
    """Get or create the agro_knowledge collection."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Agricultural knowledge documents for RAG"},
        )
        logger.info(
            f"ChromaDB collection '{COLLECTION_NAME}' ready — "
            f"{_collection.count()} documents loaded."
        )
    return _collection


def add_documents(
    documents: list[str],
    metadatas: list[dict] | None = None,
    ids: list[str] | None = None,
    embeddings: list[list[float]] | None = None,
):
    """Add documents to the vector collection."""
    collection = get_collection()
    kwargs = {"documents": documents}
    if metadatas:
        kwargs["metadatas"] = metadatas
    if ids:
        kwargs["ids"] = ids
    if embeddings:
        kwargs["embeddings"] = embeddings
    collection.add(**kwargs)
    logger.info(f"Added {len(documents)} documents to ChromaDB.")


def query_documents(
    query_texts: list[str] | None = None,
    query_embeddings: list[list[float]] | None = None,
    n_results: int = 5,
    where: dict | None = None,
) -> dict:
    """Query the vector collection and return results."""
    collection = get_collection()
    kwargs = {"n_results": n_results}
    if query_texts:
        kwargs["query_texts"] = query_texts
    if query_embeddings:
        kwargs["query_embeddings"] = query_embeddings
    if where:
        kwargs["where"] = where
    results = collection.query(**kwargs)
    return results
