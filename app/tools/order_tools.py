from langchain_core.tools import tool

from app.database.database import SessionLocal
from app.services.order_service import get_order_service


@tool
def check_order_status(order_id: int) -> dict:
    """
    Check the current status and details of a NovaCart order.

    Use this tool when a customer asks about an order,
    including whether it is processing, shipped, delivered,
    cancelled, or failed.
    """

    if order_id <= 0:
        return {
            "success": False,
            "error": "Order ID must be a positive integer.",
        }

    service = get_order_service()

    try:
        with SessionLocal() as db:

            order = service.get_order(
                db=db,
                order_id=order_id,
            )

            if order is None:
                return {
                    "success": False,
                    "error": (
                        f"Order {order_id} was not found."
                    ),
                }

            return {
                "success": True,
                "order": {
                    "order_id": order.id,
                    "customer_id": order.customer_id,
                    "product": order.product,
                    "amount": order.amount,
                    "status": order.status,
                    "tracking_number": (
                        order.tracking_number
                    ),
                    "order_date": (
                        order.order_date.isoformat()
                    ),
                    "expected_delivery_date": (
                        order.expected_delivery_date.isoformat()
                        if order.expected_delivery_date
                        else None
                    ),
                },
            }

    except Exception:
        return {
            "success": False,
            "error": (
                "Unable to retrieve order information "
                "at this time."
            ),
        }

@tool
def get_delivery_status(order_id: int) -> dict:
    """
    Get delivery and tracking information for a NovaCart order.

    Use this tool when a customer asks where an order is,
    whether it has shipped, when it is expected to arrive,
    or asks for tracking information.
    """

    if order_id <= 0:
        return {
            "success": False,
            "error": "Order ID must be a positive integer.",
        }

    service = get_order_service()

    try:
        with SessionLocal() as db:

            order = service.get_order(
                db=db,
                order_id=order_id,
            )

            if order is None:
                return {
                    "success": False,
                    "error": (
                        f"Order {order_id} was not found."
                    ),
                }

            return {
                "success": True,
                "delivery": {
                    "order_id": order.id,
                    "status": order.status,
                    "tracking_number": (
                        order.tracking_number
                    ),
                    "expected_delivery_date": (
                        order.expected_delivery_date.isoformat()
                        if order.expected_delivery_date
                        else None
                    ),
                },
            }

    except Exception:
        return {
            "success": False,
            "error": (
                "Unable to retrieve delivery information "
                "at this time."
            ),
        }        