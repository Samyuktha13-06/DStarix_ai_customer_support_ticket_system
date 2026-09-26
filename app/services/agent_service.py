import json
import logging
from langchain_core.messages import HumanMessage
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from app.services.exceptions import AgentLLMError
from app.agent.graph import build_agent_graph

logger = logging.getLogger(__name__)
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

    @staticmethod
    def _extract_order_info(messages: list, user_message: str = "", final_answer: str = "") -> dict | None:
        """
        Extract order information from LangGraph tool messages or context.
        """
        order_info = None

        for message in messages:
            if getattr(message, "type", None) != "tool":
                continue

            content = getattr(message, "content", None)
            if not content:
                continue

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

            if data.get("order_id"):
                order_info = {
                    "order_id": data["order_id"],
                    "customer_id": data.get("customer_id"),
                    "product": data.get("product"),
                    "amount": data.get("amount"),
                    "status": data.get("status"),
                    "tracking_number": data.get("tracking_number"),
                    "expected_delivery_date": data.get("expected_delivery_date"),
                }
            elif data.get("payment") and isinstance(data["payment"], dict) and data["payment"].get("order_id"):
                p = data["payment"]
                if not order_info:
                    order_info = {
                        "order_id": p["order_id"],
                        "amount": p.get("amount"),
                        "status": p.get("status"),
                    }

        # Fallback: check text for order number pattern like 45821
        if not order_info:
            import re
            match = re.search(r'(?:order|#|\*\*)\s*#?(\d{4,6})\b', user_message, re.IGNORECASE)
            if not match:
                match = re.search(r'(?:order|#|\*\*)\s*#?(\d{4,6})\b', final_answer, re.IGNORECASE)
            if match:
                order_info = {"order_id": int(match.group(1))}

        # Always enrich from database if we have an order_id
        if order_info and order_info.get("order_id"):
            try:
                from app.database.database import SessionLocal
                from app.services.order_service import get_order_service
                with SessionLocal() as db:
                    order_obj = get_order_service().get_order(db=db, order_id=order_info["order_id"])
                    if order_obj:
                        return {
                            "order_id": order_obj.id,
                            "customer_id": order_obj.customer_id,
                            "product": order_obj.product,
                            "amount": float(order_obj.amount) if order_obj.amount is not None else None,
                            "status": order_obj.status,
                            "tracking_number": order_obj.tracking_number,
                            "expected_delivery_date": (
                                str(order_obj.expected_delivery_date)
                                if order_obj.expected_delivery_date
                                else None
                            ),
                        }
            except Exception as e:
                logger.warning("Could not enrich order details from database: %s", e)

    @staticmethod
    def _extract_tools_used(messages: list) -> list[dict]:
        """
        Extract tool executions from LangGraph messages.
        """
        tools_used = []
        for message in messages:
            # Check AIMessage tool_calls
            tool_calls = getattr(message, "tool_calls", None)
            if tool_calls:
                for tc in tool_calls:
                    name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                    args = tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", {})
                    if name and not any(t["name"] == name for t in tools_used):
                        tools_used.append({"name": name, "args": args if isinstance(args, dict) else {}})

            # Check ToolMessage
            if getattr(message, "type", None) == "tool":
                name = getattr(message, "name", None)
                if name and not any(t["name"] == name for t in tools_used):
                    tools_used.append({"name": name, "args": {}})

        return tools_used

        return order_info

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

        clean_message = message.strip()
        clean_thread_id = thread_id.strip()

        logger.info(
            "Processing customer request | thread_id=%s",
            clean_thread_id,
        )

        config = {
            "configurable": {
                "thread_id": clean_thread_id
            }
        }

        try:
            result = self.graph.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content=clean_message
                        )
                    ]
                },
                config=config,
            )

        except Exception as exc:
            logger.exception(
                "Agent graph execution failed | thread_id=%s",
                clean_thread_id,
            )

            raise AgentLLMError(
                "The AI support service is temporarily unavailable."
            ) from exc

        messages = result.get("messages", [])

        if not messages:
            logger.error(
                "Agent returned no messages | thread_id=%s",
                clean_thread_id,
            )

            raise RuntimeError(
                "Agent returned no messages."
            )

        final_message = messages[-1]

        # Isolate messages produced during the CURRENT turn (from the latest HumanMessage onward)
        current_turn_messages = []
        for i in range(len(messages) - 1, -1, -1):
            msg = messages[i]
            current_turn_messages.insert(0, msg)
            if getattr(msg, "type", None) == "human" or msg.__class__.__name__ == "HumanMessage":
                break

        escalation_info = self._extract_escalation_info(
            current_turn_messages
        )

        order_info = self._extract_order_info(
            current_turn_messages,
            user_message=clean_message,
            final_answer=final_message.content,
        ) or self._extract_order_info(
            messages,
            user_message=clean_message,
            final_answer=final_message.content,
        )

        tools_used = self._extract_tools_used(current_turn_messages)

        # Extract payment info if order is present
        payment_info = None
        target_order_id = order_info["order_id"] if order_info else None
        if target_order_id:
            try:
                from app.database.database import SessionLocal
                from app.services.payment_service import get_payment_service
                with SessionLocal() as db:
                    p = get_payment_service().get_payment_for_order(db=db, order_id=target_order_id)
                    if p:
                        payment_info = {
                            "payment_id": p.id,
                            "order_id": p.order_id,
                            "amount": float(p.amount) if p.amount is not None else None,
                            "status": p.status,
                            "payment_date": p.payment_date.isoformat() if p.payment_date else None,
                        }
            except Exception as e:
                logger.warning("Could not fetch payment details: %s", e)

        logger.info(
            "Customer request completed | thread_id=%s | tools=%s | escalated=%s | ticket_id=%s | order_id=%s",
            clean_thread_id,
            [t["name"] for t in tools_used],
            escalation_info["escalated"],
            escalation_info["ticket_id"],
            order_info["order_id"] if order_info else None,
        )

        return {
            "answer": final_message.content,
            "messages": messages,
            "escalated": escalation_info["escalated"],
            "ticket_id": escalation_info["ticket_id"],
            "order": order_info,
            "payment": payment_info,
            "tools_used": tools_used,
        }



_agent_service = None


def get_agent_service() -> AgentService:
    global _agent_service

    if _agent_service is None:
        _agent_service = AgentService()

    return _agent_service