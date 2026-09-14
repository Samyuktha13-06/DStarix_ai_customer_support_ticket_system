from sqlalchemy import select
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.database.database import SessionLocal
from app.database.models import Customer, Order, Payment


def main() -> None:
    with SessionLocal() as session:

        print("\nCUSTOMERS")
        print("=" * 60)

        customers = session.scalars(
            select(Customer).order_by(Customer.id)
        ).all()

        for customer in customers:
            print(
                f"{customer.id}: "
                f"{customer.name} | "
                f"{customer.email}"
            )

        print("\nORDERS")
        print("=" * 60)

        orders = session.scalars(
            select(Order).order_by(Order.id)
        ).all()

        for order in orders:
            print(
                f"{order.id}: "
                f"{order.product} | "
                f"₹{order.amount:.2f} | "
                f"{order.status} | "
                f"Customer {order.customer_id} | "
                f"Tracking: {order.tracking_number} | "
                f"Expected: {order.expected_delivery_date}"
            )

        print("\nPAYMENTS")
        print("=" * 60)

        payments = session.scalars(
            select(Payment).order_by(Payment.id)
        ).all()

        for payment in payments:
            print(
                f"{payment.id}: "
                f"Order {payment.order_id} | "
                f"₹{payment.amount:.2f} | "
                f"{payment.status}"
            )


if __name__ == "__main__":
    main()