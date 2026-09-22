from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage

from app.agent.state import AgentState
from app.agent.llm import get_agent_llm
from scripts.test_failure_tool import controlled_failure_tool


TEST_TOOLS = [
    controlled_failure_tool,
]


def test_agent_node(state: AgentState) -> dict:
    # Get the normal Groq LLM configuration,
    # but bind only the controlled test tool.
    llm = get_agent_llm().bind_tools(TEST_TOOLS)

    messages = [
        SystemMessage(
            content="""
You are testing backend failure handling.

For this test:
- When the customer asks about an order, use controlled_failure_tool.
- Do not use any other tool.
- The controlled_failure_tool intentionally returns success=false.
- When the tool returns success=false, do not retry with another tool.
- Never invent the missing order information.
- Tell the customer that the order information could not be
  retrieved because the service is temporarily unavailable.
- Do not claim that the order was shipped, delivered, delayed,
  cancelled, or otherwise provide an unsupported status.
- Do not create or suggest a support ticket unless the customer
  explicitly requests human support.
"""
        )
    ] + state["messages"]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }


def build_test_graph():
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node(
        "agent",
        test_agent_node,
    )

    graph_builder.add_node(
        "tools",
        ToolNode(TEST_TOOLS),
    )

    graph_builder.add_edge(
        START,
        "agent",
    )

    graph_builder.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        },
    )

    graph_builder.add_edge(
        "tools",
        "agent",
    )

    return graph_builder.compile()