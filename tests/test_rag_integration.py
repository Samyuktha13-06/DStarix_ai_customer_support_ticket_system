# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from app.rag.retriever import retrieve_documents


@pytest.mark.integration
def test_refund_query_retrieval():
    documents = retrieve_documents(
        "What is the refund policy?",
        top_k=3,
    )

    assert len(documents) > 0

    sources = [
        document.metadata.get("source")
        for document in documents
    ]

    assert "refund_policy.md" in sources