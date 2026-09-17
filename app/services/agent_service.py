from langchain_core.messages import HumanMessage

from app.agent.graph import build_agent_graph


class AgentService:
    def __init__(self):
        self.graph = build_agent_graph()

    def chat(self, message: str, thread_id: str) -> dict:
        if not message or not message.strip():
            raise ValueError("Customer message cannot be empty.")

        if not thread_id or not thread_id.strip():
            raise ValueError("Thread ID cannot be empty.")

        config = {
            "configurable": {
                "thread_id": thread_id.strip()
            }
        }

        result = self.graph.invoke(
            {
                "messages": [
                    HumanMessage(content=message.strip())
                ]
            },
            config=config,
        )

        messages = result.get("messages", [])

        if not messages:
            raise RuntimeError("Agent returned no messages.")

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