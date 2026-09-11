import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.chunker import split_documents
from app.rag.loader import load_markdown_documents
from app.rag.vector_store import add_documents


def main() -> None:
    print("Loading knowledge-base documents...")

    documents = load_markdown_documents()

    print(
        f"Loaded {len(documents)} source documents."
    )

    print("Splitting documents into chunks...")

    chunks = split_documents(documents)

    print(
        f"Created {len(chunks)} document chunks."
    )

    print("Generating embeddings and storing in ChromaDB...")

    add_documents(chunks)

    print("RAG ingestion completed successfully.")


if __name__ == "__main__":
    main()