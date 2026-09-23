from langchain_core.tools import tool


@tool
def controlled_rag_no_results_tool(query: str) -> dict:
    """
    TEST TOOL ONLY.

    Use this tool to search NovaCart policies, documentation, FAQs, or
    company information when testing knowledge-base failure handling.
    Simulates a successful retrieval operation that returns
    no relevant knowledge-base documents.
    """

    return {
        "success": False,
        "error": (
            "No relevant information was found "
            "in the NovaCart knowledge base."
        ),
    }


@tool
def controlled_rag_retrieval_failure_tool(query: str) -> dict:
    """
    TEST TOOL ONLY.

    Use this tool to search NovaCart policies, documentation, FAQs, or
    company information when testing knowledge-base failure handling.
    Simulates a knowledge-base retrieval system failure.
    """

    return {
        "success": False,
        "error": (
            "The knowledge base could not be "
            "searched at this time."
        ),
    }