from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Payment


class PaymentService:

    def get_payment_for_order(
        self,
        db: Session,
        order_id: int,
    ) -> Payment | None:

        if order_id <= 0:
            raise ValueError(
                "Order ID must be a positive integer."
            )

        statement = (
            select(Payment)
            .where(Payment.order_id == order_id)
            .order_by(Payment.payment_date.desc())
        )

        return db.scalars(statement).first()


def get_payment_service() -> PaymentService:
    return PaymentService()