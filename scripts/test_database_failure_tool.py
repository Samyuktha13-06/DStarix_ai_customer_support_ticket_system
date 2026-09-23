from langchain_core.tools import tool


@tool
def controlled_database_failure_tool(order_id: int) -> dict:
    """
    TEST TOOL ONLY.

    Use this tool to retrieve order information when testing database
    failure handling. Simulates a database failure while retrieving order information.
    """
    return {
        "success": False,
        "error": "Database temporarily unavailable while retrieving order information.",
        "order_id": order_id,
    }