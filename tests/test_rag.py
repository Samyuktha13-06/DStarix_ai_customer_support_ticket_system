# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
from app.rag.chunker import split_documents
# pyrefly: ignore [missing-import]
from app.rag.loader import load_markdown_documents
# pyrefly: ignore [missing-import]
from app.rag.retriever import retrieve_documents


def test_knowledge_base_loads():
    documents = load_markdown_documents()

    assert len(documents) >= 8


def test_documents_are_chunked():
    documents = load_markdown_documents()

    chunks = split_documents(documents)

    assert len(chunks) > len(documents)


def test_chunks_have_source_metadata():
    documents = load_markdown_documents()

    chunks = split_documents(documents)

    for chunk in chunks:
        assert "source" in chunk.metadata
        assert "chunk_id" in chunk.metadata


def test_empty_query_is_rejected():
    with pytest.raises(ValueError):
        retrieve_documents("")


def test_invalid_top_k_is_rejected():
    with pytest.raises(ValueError):
        retrieve_documents(
            "What is the refund policy?",
            top_k=0,
        )