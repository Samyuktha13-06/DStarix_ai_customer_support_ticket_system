
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage

from app.agent.state import AgentState
from app.agent.llm import get_agent_llm

from scripts.test_rag_failure_tool import (
    controlled_rag_no_results_tool,
    controlled_rag_retrieval_failure_tool,
)


def build_test_rag_graph(test_tool):
    test_tools = [test_tool]

    def test_agent_node(state: AgentState) -> dict:
        llm = get_agent_llm().bind_tools(test_tools)

        messages = [
            SystemMessage(
                content=f"""
You are testing knowledge-base failure handling.

For this test:
- When the customer asks about company policies, documentation, or FAQs, use {test_tool.name}.
- Do not use any other tool.
- The {test_tool.name} intentionally returns success=false.
- When the tool returns success=false, do not retry.
- Never invent NovaCart policies or product information.
- Clearly explain that the requested information could
  not be retrieved.
- Do not create a support ticket unless the customer
  explicitly requests human support.
"""
            )
        ] + state["messages"]

        response = llm.invoke(messages)

        return {
            "messages": [response]
        }

    graph_builder = StateGraph(AgentState)

    graph_builder.add_node(
        "agent",
        test_agent_node,
    )

    graph_builder.add_node(
        "tools",
        ToolNode(test_tools),
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