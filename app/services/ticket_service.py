from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Ticket


class TicketService:

    def create_ticket(
        self,
        db: Session,
        customer_id: int,
        subject: str,
        description: str,
        priority: str = "normal",
        order_id: int | None = None,
    ) -> Ticket:

        if customer_id <= 0:
            raise ValueError(
                "Customer ID must be a positive integer."
            )

        if not subject.strip():
            raise ValueError(
                "Ticket subject cannot be empty."
            )

        if not description.strip():
            raise ValueError(
                "Ticket description cannot be empty."
            )

        allowed_priorities = {
            "low",
            "normal",
            "high",
            "urgent",
        }

        if priority not in allowed_priorities:
            raise ValueError(
                "Invalid ticket priority."
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
        self,
        db: Session,
        ticket_id: int,
    ) -> Ticket | None:

        if ticket_id <= 0:
            raise ValueError(
                "Ticket ID must be a positive integer."
            )

        statement = select(Ticket).where(
            Ticket.id == ticket_id
        )

        return db.scalar(statement)


def get_ticket_service() -> TicketService:
    return TicketService()