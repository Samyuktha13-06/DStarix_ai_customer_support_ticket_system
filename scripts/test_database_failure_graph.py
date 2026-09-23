from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.agent.state import AgentState
from app.agent.llm import get_agent_llm
from scripts.test_database_failure_tool import (
    controlled_database_failure_tool,
)


TEST_TOOLS = [controlled_database_failure_tool]


def agent_node(state: AgentState) -> dict:
    """
    Test-only agent node.

    Binds only the controlled database failure tool.
    """
    llm = get_agent_llm().bind_tools(TEST_TOOLS)

    messages = [
        SystemMessage(
            content="""
You are testing database failure handling.

For this test:
- When the customer asks about an order, use controlled_database_failure_tool.
- Do not use any other tool.
- The controlled_database_failure_tool intentionally returns success=false.
- When the tool returns success=false, do not retry with another tool.
- Never invent order information or order status.
- Tell the customer that the order information could not be retrieved because the database is temporarily unavailable.
- Do not claim that the order was shipped, delivered, delayed, cancelled, or in transit.
"""
        )
    ] + state["messages"]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }


def should_continue(state: AgentState):
    """
    Continue to tools if the LLM requested a tool call.
    Otherwise finish.
    """
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return END


def build_test_graph():
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TEST_TOOLS))

    graph.add_edge(START, "agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )

    graph.add_edge("tools", "agent")

    return graph.compile()


def main():
    print("=" * 80)
    print("PHASE 9.5 - DATABASE FAILURE TEST")
    print("=" * 80)

    graph = build_test_graph()

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="Please check the status of order 45821."
                )
            ]
        }
    )

    messages = result["messages"]

    print("\nMESSAGES:")
    for message in messages:
        print(f"\nTYPE: {message.type}")
        print(f"CONTENT: {message.content}")

        if getattr(message, "tool_calls", None):
            print(f"TOOL CALLS: {message.tool_calls}")

    tool_messages = [
        message
        for message in messages
        if message.type == "tool"
    ]

    assert len(tool_messages) == 1, (
        f"Expected exactly one tool call, got {len(tool_messages)}"
    )

    tool_message = tool_messages[0]

    assert "success" in tool_message.content
    assert "Database temporarily unavailable" in tool_message.content

    final_message = messages[-1]

    assert final_message.type == "ai"

    final_content = final_message.content.lower()

    # The model must not fabricate an actual order status.
    forbidden_statuses = [
        "shipped",
        "delivered",
        "processing",
        "cancelled",
        "in transit",
    ]

    for status in forbidden_statuses:
        assert status not in final_content, (
            f"Possible fabricated order status detected: {status}"
        )

    print("\nPASS: Database failure was returned as a controlled tool failure.")
    print("PASS: Exactly one database-failure tool call occurred.")
    print("PASS: Agent produced a final response.")
    print("PASS: No fabricated order status was returned.")

    print("\n" + "=" * 80)
    print("PHASE 9.5 DATABASE FAILURE TEST: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()