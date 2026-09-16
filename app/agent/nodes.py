from langchain_core.messages import SystemMessage

from app.agent.llm import get_agent_llm
from app.agent.prompts import AGENT_SYSTEM_PROMPT
from app.agent.state import AgentState


def agent_node(state: AgentState) -> dict:
    llm = get_agent_llm()

    messages = [
        SystemMessage(
            content=AGENT_SYSTEM_PROMPT
        )
    ] + state["messages"]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }