from langchain_core.tools import tool
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from app.database.database import SessionLocal
from app.services.ticket_service import create_ticket
from app.services.order_service import get_order_service

@tool
def create_support_ticket(
    customer_id: int,
    subject: str,
    description: str,
    priority: str = "normal",
    order_id: int | None = None,
) -> dict:
    """
    Create a support ticket for a customer issue.
    """

    try:
        with SessionLocal() as db:
            ticket = create_ticket(
                db=db,
                customer_id=customer_id,
                subject=subject,
                description=description,
                priority=priority,
                order_id=order_id,
            )

            return {
                "success": True,
                "ticket_id": ticket.id,
                "customer_id": ticket.customer_id,
                "order_id": ticket.order_id,
                "subject": ticket.subject,
                "priority": ticket.priority,
                "status": ticket.status,
                "message": (
                    f"Support ticket {ticket.id} "
                    f"created successfully."
                ),
            }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }


@tool
def escalate_to_human(
    customer_id: int | None = None,
    reason: str = "",
    order_id: int | None = None,
    priority: str = "high",
) -> dict:
    """
    Escalate a customer issue to human support by creating a support ticket.

    If customer_id is not provided but order_id is available, the customer
    ID is safely retrieved from the order database.
    """

    try:
        if not reason or not reason.strip():
            return {
                "success": False,
                "escalated": False,
                "error": "Escalation reason cannot be empty.",
            }

        with SessionLocal() as db:

            # If customer_id is missing, derive it from the order.
            if customer_id is None:

                if order_id is None:
                    return {
                        "success": False,
                        "escalated": False,
                        "error": (
                            "Customer ID or a valid order ID "
                            "is required for escalation."
                        ),
                    }

                order_service = get_order_service()

                order = order_service.get_order(
                    db=db,
                    order_id=order_id,
                )

                if order is None:
                    return {
                        "success": False,
                        "escalated": False,
                        "error": (
                            f"Order {order_id} was not found. "
                            "Unable to determine the customer."
                        ),
                    }

                customer_id = order.customer_id

            ticket = create_ticket(
                db=db,
                customer_id=customer_id,
                subject="Human support escalation",
                description=reason.strip(),
                priority=priority,
                order_id=order_id,
            )

            return {
                "success": True,
                "escalated": True,
                "ticket_id": ticket.id,
                "customer_id": ticket.customer_id,
                "order_id": ticket.order_id,
                "priority": ticket.priority,
                "status": ticket.status,
                "reason": ticket.description,
                "message": (
                    "Issue successfully escalated to human support. "
                    f"Ticket ID: {ticket.id}."
                ),
            }

    except Exception as exc:
        return {
            "success": False,
            "escalated": False,
            "error": str(exc),
        }