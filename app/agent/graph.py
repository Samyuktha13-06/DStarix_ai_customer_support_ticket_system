from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from app.agent.state import AgentState
from app.agent.nodes import agent_node
from app.agent.tools import AGENT_TOOLS


def build_agent_graph():
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("agent", agent_node)
    graph_builder.add_node("tools", ToolNode(AGENT_TOOLS))

    graph_builder.add_edge(START, "agent")

    graph_builder.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        },
    )

    graph_builder.add_edge("tools", "agent")

    # Conversation memory
    memory = MemorySaver()

    return graph_builder.compile(checkpointer=memory)