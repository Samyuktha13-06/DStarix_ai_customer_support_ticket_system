import sys
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


from app.services.rag_generation_service import (
    get_rag_generation_service,
)


def main() -> None:

    service = get_rag_generation_service()

    queries = [
        "What is the refund policy?",
        "How long does standard delivery take?",
        "Can I cancel my order after it has shipped?",
        "What happens if my payment was deducted but my order failed?",
        "What is the capital of France?"
    ]

    for query in queries:

        print("\n" + "=" * 80)
        print(f"QUESTION: {query}")
        print("=" * 80)

        try:
            result = service.generate_answer(
                query=query,
                top_k=4,
            )

            print("\nANSWER:")
            print(result["answer"])

            print("\nSOURCES:")

            for source in result["sources"]:
                print(
                    f"- {source['source']} "
                    f"(chunk {source['chunk_id']})"
                )

        except Exception as exc:
            print(f"ERROR: {exc}")


if __name__ == "__main__":
    main()