# pyrefly: ignore [missing-import]
from langchain_core.documents import Document

from app.rag.retriever import retrieve_documents


class RetrievalService:
    """
    Application-level service for knowledge retrieval.
    """

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
    ) -> list[Document]:
        return retrieve_documents(
            query=query,
            top_k=top_k,
        )


def get_retrieval_service() -> RetrievalService:
    return RetrievalService()