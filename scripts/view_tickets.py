from sqlalchemy import select
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import SessionLocal
from app.database.models import Ticket


def main() -> None:
    with SessionLocal() as session:

        tickets = session.scalars(
            select(Ticket).order_by(Ticket.id)
        ).all()

        if not tickets:
            print("No support tickets found.")
            return

        print("\nSUPPORT TICKETS")
        print("=" * 80)

        for ticket in tickets:
            print(f"Ticket ID   : {ticket.id}")
            print(f"Customer ID : {ticket.customer_id}")
            print(f"Order ID    : {ticket.order_id}")
            print(f"Subject     : {ticket.subject}")
            print(f"Description : {ticket.description}")
            print(f"Priority    : {ticket.priority}")
            print(f"Status      : {ticket.status}")
            print(f"Created At  : {ticket.created_at}")
            print("-" * 80)


if __name__ == "__main__":
    main()