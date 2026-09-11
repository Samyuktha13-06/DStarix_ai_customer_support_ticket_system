# pyrefly: ignore [missing-import]
from langchain_core.documents import Document


def retrieve_documents(
    query: str,
    top_k: int = 4,
) -> list[Document]:
    """
    Retrieve the most relevant knowledge-base chunks
    for a user query.
    """

    if not query or not query.strip():
        raise ValueError(
            "Retrieval query cannot be empty."
        )

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than zero."
        )

    from app.rag.vector_store import get_vector_store

    vector_store = get_vector_store()

    documents = vector_store.similarity_search(
        query,
        k=top_k,
    )

    return documents

def retrieve_documents_with_scores(
    query: str,
    top_k: int = 4,
) -> list[tuple[Document, float]]:
    """
    Retrieve relevant documents along with their
    similarity scores.
    """

    if not query or not query.strip():
        raise ValueError(
            "Retrieval query cannot be empty."
        )

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than zero."
        )

    from app.rag.vector_store import get_vector_store

    vector_store = get_vector_store()

    return vector_store.similarity_search_with_score(
        query,
        k=top_k,
    )