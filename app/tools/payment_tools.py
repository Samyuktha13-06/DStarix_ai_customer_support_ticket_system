from langchain_core.tools import tool

from app.database.database import SessionLocal
from app.services.payment_service import get_payment_service


@tool
def check_payment_status(order_id: int) -> dict:
    """
    Check the latest payment status for a NovaCart order.

    Use this tool when a customer asks about a payment,
    including failed, captured, pending, refunded, or
    partially refunded payments.
    """

    if order_id <= 0:
        return {
            "success": False,
            "error": "Order ID must be a positive integer.",
        }

    service = get_payment_service()

    try:
        with SessionLocal() as db:

            payment = service.get_payment_for_order(
                db=db,
                order_id=order_id,
            )

            if payment is None:
                return {
                    "success": False,
                    "error": (
                        f"No payment record was found "
                        f"for order {order_id}."
                    ),
                }

            return {
                "success": True,
                "payment": {
                    "payment_id": payment.id,
                    "order_id": payment.order_id,
                    "amount": payment.amount,
                    "status": payment.status,
                    "payment_date": (
                        payment.payment_date.isoformat()
                    ),
                },
            }

    except Exception:
        return {
            "success": False,
            "error": (
                "Unable to retrieve payment information "
                "at this time."
            ),
        }