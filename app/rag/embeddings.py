from functools import lru_cache

# pyrefly: ignore [missing-import]
from langchain_huggingface import HuggingFaceEmbeddings


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache
def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Create and cache the local embedding model.
    """

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu",
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )