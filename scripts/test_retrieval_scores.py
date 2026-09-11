from pathlib import Path
import sys

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.retriever import (
    retrieve_documents_with_scores,
)


def main() -> None:
    query = "What is your refund policy?"

    results = retrieve_documents_with_scores(
        query,
        top_k=5,
    )

    print(f"\nQuery: {query}\n")

    for index, (document, score) in enumerate(
        results,
        start=1,
    ):
        print(f"Result {index}")
        print(
            f"Source: "
            f"{document.metadata.get('source')}"
        )
        print(f"Score: {score:.4f}")
        print(
            f"Content: "
            f"{document.page_content[:300]}"
        )
        print("-" * 60)


if __name__ == "__main__":
    main()