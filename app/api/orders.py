from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import sys 
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.database.database import SessionLocal
from app.services.order_service import get_order_service


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class OrderResponse(BaseModel):
    order_id: int
    customer_id: int
    product: str
    amount: float
    status: str
    tracking_number: str | None = None
    expected_delivery_date: date | None = None


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order information",
    description="Retrieve order information using the order ID.",
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    try:
        order_service = get_order_service()
        order = order_service.get_order(
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
            detail="Unable to retrieve order information.",
        ) from exc

    if order is None:
        raise HTTPException(
            status_code=404,
            detail=f"Order {order_id} was not found.",
        )

    return OrderResponse(
        order_id=order.id,
        customer_id=order.customer_id,
        product=order.product,
        amount=float(order.amount),
        status=order.status,
        tracking_number=order.tracking_number,
        expected_delivery_date=order.expected_delivery_date,
    )