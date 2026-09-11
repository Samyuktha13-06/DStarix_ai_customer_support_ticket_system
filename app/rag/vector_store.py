from functools import lru_cache

# pyrefly: ignore [missing-import]
from langchain_chroma import Chroma
# pyrefly: ignore [missing-import]
from langchain_core.documents import Document

from app.rag.embeddings import get_embedding_model


CHROMA_DIRECTORY = "./data/chroma"
COLLECTION_NAME = "novacart_knowledge_base"


@lru_cache
def get_vector_store() -> Chroma:
    """
    Return the persistent NovaCart Chroma vector store.
    """

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=CHROMA_DIRECTORY,
    )


def add_documents(
    documents: list[Document],
) -> None:
    """
    Add document chunks to ChromaDB.
    """

    if not documents:
        raise ValueError(
            "Cannot add an empty document list to ChromaDB."
        )

    vector_store = get_vector_store()

    vector_store.add_documents(
        documents=documents
    )