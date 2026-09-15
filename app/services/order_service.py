from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Order


class OrderService:

    def get_order(
        self,
        db: Session,
        order_id: int,
    ) -> Order | None:

        if order_id <= 0:
            raise ValueError(
                "Order ID must be a positive integer."
            )

        statement = select(Order).where(
            Order.id == order_id
        )

        return db.scalar(statement)


def get_order_service() -> OrderService:
    return OrderService()