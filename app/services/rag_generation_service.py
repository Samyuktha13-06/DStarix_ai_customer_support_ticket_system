# pyrefly: ignore [missing-import]
from langchain_core.documents import Document

from app.llm.groq_client import get_llm
from app.rag.prompt import RAG_PROMPT
from app.rag.retriever import retrieve_documents


class RAGGenerationService:

    def retrieve_context(
        self,
        query: str,
        top_k: int = 4,
    ) -> list[Document]:

        return retrieve_documents(
            query=query,
            top_k=top_k,
        )

    def build_context(
        self,
        documents: list[Document],
    ) -> str:

        if not documents:
            return ""

        context_parts = []

        for document in documents:
            source = document.metadata.get(
                "source",
                "unknown",
            )

            chunk_id = document.metadata.get(
                "chunk_id",
                "unknown",
            )

            context_parts.append(
                f"""
Source: {source}
Chunk ID: {chunk_id}

{document.page_content}
"""
            )

        return "\n---\n".join(context_parts)

    def generate_answer(
        self,
        query: str,
        top_k: int = 4,
    ) -> dict:

        if not query or not query.strip():
            raise ValueError(
                "Customer query cannot be empty."
            )

        documents = self.retrieve_context(
            query=query,
            top_k=top_k,
        )

        if not documents:
            return {
                "answer": (
                    "I could not find enough information in "
                    "the NovaCart knowledge base to answer "
                    "your question."
                ),
                "sources": [],
            }

        context = self.build_context(documents)

        prompt = RAG_PROMPT.invoke(
            {
                "context": context,
                "question": query,
            }
        )

        llm = get_llm()

        response = llm.invoke(prompt)

        sources = []

        for document in documents:
            sources.append(
                {
                    "source": document.metadata.get(
                        "source"
                    ),
                    "chunk_id": document.metadata.get(
                        "chunk_id"
                    ),
                }
            )

        return {
            "answer": response.content,
            "sources": sources,
        }


def get_rag_generation_service() -> RAGGenerationService:
    return RAGGenerationService()