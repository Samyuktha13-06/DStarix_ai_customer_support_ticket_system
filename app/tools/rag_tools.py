from langchain_core.tools import tool

from app.rag.retriever import retrieve_documents


@tool
def search_knowledge_base(query: str) -> dict:
    """
    Search the NovaCart knowledge base for company policies,
    FAQs, product information, shipping information, payment
    policies, cancellation rules, refund rules, and account
    support information.

    Use this tool when the customer asks a question that can
    be answered using NovaCart's documentation rather than
    live customer or order data.
    """

    if not query or not query.strip():
        return {
            "success": False,
            "error": "Knowledge-base query cannot be empty.",
        }

    try:
        documents = retrieve_documents(
            query=query,
            top_k=4,
        )

        if not documents:
            return {
                "success": False,
                "error": (
                    "No relevant information was found "
                    "in the NovaCart knowledge base."
                ),
            }

        results = []

        for document in documents:
            results.append(
                {
                    "source": document.metadata.get(
                        "source"
                    ),
                    "chunk_id": document.metadata.get(
                        "chunk_id"
                    ),
                    "content": document.page_content,
                }
            )

        return {
            "success": True,
            "results": results,
        }

    except Exception:
        return {
            "success": False,
            "error": (
                "The knowledge base could not be "
                "searched at this time."
            ),
        }