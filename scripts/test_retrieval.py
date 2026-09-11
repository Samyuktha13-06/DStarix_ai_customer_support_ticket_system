
from pathlib import Path
import sys

#Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.retriever import retrieve_documents

def main() -> None:
    queries = [
        "What is the refund policy?",
        "How long does standard delivery take?",
        "What happens if my payment was deducted but my order failed?",
        "Can I cancel my order after it has shipped?",
        "What should I do if my account is compromised?",
    ]

    for query in queries:
        print("\n" + "=" * 80)
        print(f"QUERY: {query}")
        print("=" * 80)

        documents = retrieve_documents(
            query,
            top_k=3,
        )

        if not documents:
            print("No relevant documents found.")
            continue

        for index, document in enumerate(
            documents,
            start=1,
        ):
            print(f"\nRESULT {index}")
            print(
                f"Source: "
                f"{document.metadata.get('source')}"
            )
            print(
                f"Chunk ID: "
                f"{document.metadata.get('chunk_id')}"
            )
            print(
                f"Content:\n"
                f"{document.page_content[:500]}"
            )


if __name__ == "__main__":
    main()