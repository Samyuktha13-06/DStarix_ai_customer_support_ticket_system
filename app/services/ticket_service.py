from sqlalchemy.orm import Session
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from app.database.models import Ticket


ALLOWED_PRIORITIES = {
    "low",
    "normal",
    "high",
    "urgent",
}


def create_ticket(
    db: Session,
    customer_id: int,
    subject: str,
    description: str,
    priority: str = "normal",
    order_id: int | None = None,
) -> Ticket:

    if customer_id <= 0:
        raise ValueError("Customer ID must be positive.")

    if not subject or not subject.strip():
        raise ValueError("Ticket subject cannot be empty.")

    if not description or not description.strip():
        raise ValueError("Ticket description cannot be empty.")

    priority = priority.lower().strip()

    if priority not in ALLOWED_PRIORITIES:
        raise ValueError(
            f"Invalid priority. Allowed values: "
            f"{', '.join(sorted(ALLOWED_PRIORITIES))}"
        )

    ticket = Ticket(
        customer_id=customer_id,
        order_id=order_id,
        subject=subject.strip(),
        description=description.strip(),
        priority=priority,
        status="open",
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


def get_ticket(
    db: Session,
    ticket_id: int,
) -> Ticket | None:

    if ticket_id <= 0:
        raise ValueError("Ticket ID must be positive.")

    return db.get(Ticket, ticket_id)