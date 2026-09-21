from langchain_core.tools import tool
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from app.database.database import SessionLocal
from app.services.ticket_service import create_ticket


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
    customer_id: int,
    reason: str,
    order_id: int | None = None,
    priority: str = "high",
) -> dict:
    """
    Escalate a customer issue to human support by creating a ticket.
    """

    try:
        if not reason or not reason.strip():
            return {
                "success": False,
                "error": "Escalation reason cannot be empty.",
            }

        with SessionLocal() as db:
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
                    f"Issue successfully escalated to human support. "
                    f"Ticket ID: {ticket.id}."
                ),
            }

    except Exception as exc:
        return {
            "success": False,
            "escalated": False,
            "error": str(exc),
        }