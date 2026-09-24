import logging
import math
import re
from functools import lru_cache

# pyrefly: ignore [missing-import]
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_cached_chunks() -> list[Document]:
    """
    Load and cache document chunks directly from knowledge base markdown files.
    """
    try:
        from app.rag.loader import load_markdown_documents
        from app.rag.chunker import split_documents

        docs = load_markdown_documents()
        return split_documents(docs)
    except Exception as exc:
        logger.error("Failed to load documents for lexical retrieval: %s", exc)
        return []


def _lexical_search(query: str, top_k: int = 4) -> list[Document]:
    """
    Pure-Python fallback search across knowledge-base document chunks.
    Ensures knowledge retrieval always succeeds even when C-extension DLLs
    (e.g., scipy / sentence-transformers) are blocked by Windows Application Control.
    """
    chunks = get_cached_chunks()
    if not chunks:
        return []

    q_tokens = [
        w.lower() for w in re.findall(r"\b[a-zA-Z0-9_\-]+\b", query) if len(w) > 1
    ]
    stop_words = {
        "what", "is", "the", "a", "an", "in", "of", "to", "for", "and", "or",
        "our", "my", "your", "can", "how", "do", "i", "does", "are", "about",
    }
    query_terms = [t for t in q_tokens if t not in stop_words] or q_tokens

    scores = []
    for chunk in chunks:
        content = chunk.page_content.lower()
        source = chunk.metadata.get("source", "").lower()

        score = 0.0
        for term in query_terms:
            if term in source:
                score += 6.0

            count = content.count(term)
            if count > 0:
                score += 1.0 + math.log(1 + count)
            elif any(
                term in word or word in term
                for word in content.split()
                if len(word) > 2
            ):
                score += 0.5

        scores.append((score, chunk))

    scores.sort(key=lambda x: x[0], reverse=True)
    results = [chunk for score, chunk in scores[:top_k] if score > 0]
    return results or [c for _, c in scores[:top_k]]


def retrieve_documents(
    query: str,
    top_k: int = 4,
) -> list[Document]:
    """
    Retrieve the most relevant knowledge-base chunks for a user query.
    Tries persistent vector store first, with seamless pure-Python fallback.
    """
    if not query or not query.strip():
        raise ValueError("Retrieval query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    try:
        from app.rag.vector_store import get_vector_store

        vector_store = get_vector_store()
        documents = vector_store.similarity_search(
            query,
            k=top_k,
        )
        if documents:
            return documents
    except Exception as exc:
        logger.warning(
            "Vector store retrieval unavailable (%s). Using direct knowledge-base search.",
            exc,
        )

    return _lexical_search(query=query, top_k=top_k)


def retrieve_documents_with_scores(
    query: str,
    top_k: int = 4,
) -> list[tuple[Document, float]]:
    """
    Retrieve relevant documents along with their similarity scores.
    """
    if not query or not query.strip():
        raise ValueError("Retrieval query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    try:
        from app.rag.vector_store import get_vector_store

        vector_store = get_vector_store()
        results = vector_store.similarity_search_with_score(
            query,
            k=top_k,
        )
        if results:
            return results
    except Exception as exc:
        logger.warning(
            "Vector store retrieval with score unavailable (%s). Using fallback.",
            exc,
        )

    docs = _lexical_search(query=query, top_k=top_k)
    return [(doc, 0.9 - idx * 0.1) for idx, doc in enumerate(docs)]