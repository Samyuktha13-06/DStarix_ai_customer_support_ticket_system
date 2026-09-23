import json

from langchain_core.messages import HumanMessage
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from app.services.exceptions import AgentLLMError
from app.agent.graph import build_agent_graph


class AgentService:

    def __init__(self):
        self.graph = build_agent_graph()

    @staticmethod
    def _extract_escalation_info(messages: list) -> dict:
        """
        Extract escalation information from LangGraph tool messages.

        Returns:
            {
                "escalated": bool,
                "ticket_id": int | None
            }
        """

        escalated = False
        ticket_id = None

        for message in messages:

            # ToolMessage objects have type == "tool"
            if getattr(message, "type", None) != "tool":
                continue

            content = getattr(message, "content", None)

            if not content:
                continue

            # Tool results are normally JSON strings.
            try:
                if isinstance(content, str):
                    data = json.loads(content)
                elif isinstance(content, dict):
                    data = content
                else:
                    continue

            except (json.JSONDecodeError, TypeError):
                continue

            if not isinstance(data, dict):
                continue

            # Only treat a successful escalation as an escalation.
            if data.get("escalated") is True:
                escalated = True

                if data.get("ticket_id") is not None:
                    ticket_id = data["ticket_id"]

        return {
            "escalated": escalated,
            "ticket_id": ticket_id,
        }

    def chat(
        self,
        message: str,
        thread_id: str,
    ) -> dict:

        if not message or not message.strip():
            raise ValueError(
                "Customer message cannot be empty."
            )

        if not thread_id or not thread_id.strip():
            raise ValueError(
                "Thread ID cannot be empty."
            )

        config = {
            "configurable": {
                "thread_id": thread_id.strip()
            }
        }

        try:
            result = self.graph.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content=message.strip()
                        )
            ]
        },
        config=config,
    )

        except Exception as exc:    
            raise AgentLLMError(
                "The AI support service is temporarily unavailable."
            ) from exc

        messages = result.get("messages", [])

        if not messages:
            raise RuntimeError(
                "Agent returned no messages."
            )

        final_message = messages[-1]

        escalation_info = self._extract_escalation_info(
            messages
        )

        return {
            "answer": final_message.content,
            "messages": messages,
            "escalated": escalation_info["escalated"],
            "ticket_id": escalation_info["ticket_id"],
        }


_agent_service = None


def get_agent_service() -> AgentService:
    global _agent_service

    if _agent_service is None:
        _agent_service = AgentService()

    return _agent_service