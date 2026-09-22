from langchain_core.tools import tool


@tool
def controlled_failure_tool(order_id: int) -> dict:
    """
    TEST TOOL ONLY.

    Use this tool to retrieve order status when testing backend
    failure handling. This tool intentionally simulates a backend
    service failure and always returns success=false.
    """

    return {
        "success": False,
        "error": (
            "Controlled test failure: "
            "order service is temporarily unavailable."
        ),
        "order_id": order_id,
    }