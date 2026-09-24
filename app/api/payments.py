from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import sys 
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.database.database import SessionLocal
from app.services.payment_service import get_payment_service


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class PaymentResponse(BaseModel):
    payment_id: int
    order_id: int
    amount: float
    status: str
    payment_date: datetime


@router.get(
    "/{order_id}",
    response_model=PaymentResponse,
    summary="Get payment information",
    description=(
        "Retrieve the latest payment information associated "
        "with a NovaCart order."
    ),
)
def get_payment(
    order_id: int,
    db: Session = Depends(get_db),
):
    try:
        payment_service = get_payment_service()

        payment = payment_service.get_payment_for_order(
            db=db,
            order_id=order_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve payment information.",
        ) from exc

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail=f"No payment record was found for order {order_id}.",
        )

    return PaymentResponse(
        payment_id=payment.id,
        order_id=payment.order_id,
        amount=float(payment.amount),
        status=payment.status,
        payment_date=payment.payment_date,
    )