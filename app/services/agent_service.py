from pathlib import Path
import sys


sys.path.append(str(Path(__file__).parent.parent))


from langchain_core.messages import HumanMessage

from app.agent.graph import build_agent_graph


class AgentService:

    def __init__(self):
        self.graph = build_agent_graph()

    def chat(self, message: str) -> dict:
        if not message or not message.strip():
            raise ValueError(
                "Customer message cannot be empty."
            )

        result = self.graph.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=message.strip()
                    )
                ]
            }
        )

        messages = result.get("messages", [])

        if not messages:
            raise RuntimeError(
                "Agent returned no messages."
            )

        final_message = messages[-1]

        return {
            "answer": final_message.content,
            "messages": messages,
        }


_agent_service = None


def get_agent_service() -> AgentService:
    global _agent_service

    if _agent_service is None:
        _agent_service = AgentService()

    return _agent_service