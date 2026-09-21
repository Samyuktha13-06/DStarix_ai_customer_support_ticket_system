from langchain_core.tools import tool
import sys

from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from app.database.database import SessionLocal
from app.services.order_service import get_order_service


@tool
def check_order_status(order_id: int) -> dict:
    """
    Check the current status and details of a customer order.
    """

    try:
        with SessionLocal() as db:

            # Get the service object first.
            order_service = get_order_service()

            # Then call the service method.
            order = order_service.get_order(
                db=db,
                order_id=order_id,
            )

            if order is None:
                return {
                    "success": False,
                    "error": f"Order {order_id} was not found.",
                }

            return {
                "success": True,
                "order_id": order.id,
                "customer_id": order.customer_id,
                "product": order.product,
                "amount": float(order.amount),
                "status": order.status,
                "tracking_number": order.tracking_number,
                "expected_delivery_date": (
                    str(order.expected_delivery_date)
                    if order.expected_delivery_date
                    else None
                ),
            }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }


@tool
def get_delivery_status(order_id: int) -> dict:
    """
    Get delivery information for an order.
    """

    try:
        with SessionLocal() as db:

            order_service = get_order_service()

            order = order_service.get_order(
                db=db,
                order_id=order_id,
            )

            if order is None:
                return {
                    "success": False,
                    "error": f"Order {order_id} was not found.",
                }

            return {
                "success": True,
                "order_id": order.id,
                "customer_id": order.customer_id,
                "status": order.status,
                "tracking_number": order.tracking_number,
                "expected_delivery_date": (
                    str(order.expected_delivery_date)
                    if order.expected_delivery_date
                    else None
                ),
            }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }