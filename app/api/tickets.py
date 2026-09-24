from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.database.database import SessionLocal
from app.services.ticket_service import (
    create_ticket,
    get_ticket,
)

router = APIRouter()


class TicketCreateRequest(BaseModel):
    customer_id: int
    subject: str
    description: str
    priority: str = "normal"
    order_id: int | None = None


@router.get("/tickets")
def list_tickets_api(customer_id: int | None = None):
    from app.database.models import Ticket
    try:
        with SessionLocal() as db:
            query = db.query(Ticket)
            if customer_id is not None:
                query = query.filter(Ticket.customer_id == customer_id)
            tickets = query.order_by(Ticket.id.desc()).limit(20).all()
            return [
                {
                    "ticket_id": t.id,
                    "customer_id": t.customer_id,
                    "order_id": t.order_id,
                    "subject": t.subject,
                    "description": t.description,
                    "priority": t.priority,
                    "status": t.status,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
                for t in tickets
            ]
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to list tickets at this time.",
        )


@router.post("/tickets")
def create_ticket_api(request: TicketCreateRequest):

    try:
        with SessionLocal() as db:

            ticket = create_ticket(
                db=db,
                customer_id=request.customer_id,
                subject=request.subject,
                description=request.description,
                priority=request.priority,
                order_id=request.order_id,
            )

            return {
                "ticket_id": ticket.id,
                "customer_id": ticket.customer_id,
                "order_id": ticket.order_id,
                "subject": ticket.subject,
                "description": ticket.description,
                "priority": ticket.priority,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat(),
            }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to create support ticket at this time.",
        )


@router.get("/tickets/{ticket_id}")
def get_ticket_api(ticket_id: int):

    try:
        with SessionLocal() as db:

            ticket = get_ticket(
                db=db,
                ticket_id=ticket_id,
            )

            if ticket is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Ticket {ticket_id} was not found.",
                )

            return {
                "ticket_id": ticket.id,
                "customer_id": ticket.customer_id,
                "order_id": ticket.order_id,
                "subject": ticket.subject,
                "description": ticket.description,
                "priority": ticket.priority,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat(),
            }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve ticket at this time.",
        )