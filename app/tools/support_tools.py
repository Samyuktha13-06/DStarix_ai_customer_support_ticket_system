from langchain_core.tools import tool
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import SessionLocal
from app.services.ticket_service import (
    get_ticket_service,
)


@tool
def create_support_ticket(
    customer_id: int,
    subject: str,
    description: str,
    priority: str = "normal",
    order_id: int | None = None,
) -> dict:
    """
    Create a NovaCart customer-support ticket.

    Use this tool when an issue requires support intervention,
    manual investigation, or a customer explicitly requests
    a support ticket.
    """

    if customer_id <= 0:
        return {
            "success": False,
            "error": (
                "Customer ID must be a positive integer."
            ),
        }

    service = get_ticket_service()

    try:
        with SessionLocal() as db:

            ticket = service.create_ticket(
                db=db,
                customer_id=customer_id,
                subject=subject,
                description=description,
                priority=priority,
                order_id=order_id,
            )

            return {
                "success": True,
                "ticket": {
                    "ticket_id": ticket.id,
                    "customer_id": (
                        ticket.customer_id
                    ),
                    "order_id": ticket.order_id,
                    "subject": ticket.subject,
                    "priority": ticket.priority,
                    "status": ticket.status,
                    "created_at": (
                        ticket.created_at.isoformat()
                    ),
                },
            }

    except ValueError as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    except Exception:
        return {
            "success": False,
            "error": (
                "Unable to create a support ticket "
                "at this time."
            ),
        }

@tool
def escalate_to_human(
    customer_id: int,
    reason: str,
    order_id: int | None = None,
    priority: str = "high",
) -> dict:
    """
    Escalate a customer issue to human NovaCart support.

    Use this when the customer explicitly requests a human,
    the issue requires manual investigation, a tool failure
    prevents resolution, or the issue involves a policy
    exception or potentially unauthorized transaction.
    """

    if customer_id <= 0:
        return {
            "success": False,
            "error": (
                "Customer ID must be a positive integer."
            ),
        }

    if not reason or not reason.strip():
        return {
            "success": False,
            "error": "Escalation reason cannot be empty.",
        }

    service = get_ticket_service()

    try:
        with SessionLocal() as db:

            ticket = service.create_ticket(
                db=db,
                customer_id=customer_id,
                subject="Human support escalation",
                description=reason,
                priority=priority,
                order_id=order_id,
            )

            return {
                "success": True,
                "message": (
                    "The issue has been escalated "
                    "to human support."
                ),
                "ticket": {
                    "ticket_id": ticket.id,
                    "customer_id": (
                        ticket.customer_id
                    ),
                    "order_id": ticket.order_id,
                    "priority": ticket.priority,
                    "status": ticket.status,
                },
            }

    except ValueError as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    except Exception:
        return {
            "success": False,
            "error": (
                "Unable to escalate the issue "
                "at this time."
            ),
        }