from datetime import date, datetime, timedelta

from sqlalchemy import select
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import SessionLocal
from app.database.models import Customer, Order, Payment


def seed_database() -> None:
    with SessionLocal() as session:

        existing_customer = session.scalar(
            select(Customer).limit(1)
        )

        if existing_customer is not None:
            print(
                "Database already contains customer data. "
                "Skipping seed operation."
            )
            return

        # -------------------------------------------------
        # Customers
        # -------------------------------------------------

        customers = [
            Customer(
                name="Aarav Sharma",
                email="aarav.sharma@example.com",
            ),
            Customer(
                name="Priya Nair",
                email="priya.nair@example.com",
            ),
            Customer(
                name="Rahul Mehta",
                email="rahul.mehta@example.com",
            ),
            Customer(
                name="Ananya Reddy",
                email="ananya.reddy@example.com",
            ),
        ]

        session.add_all(customers)
        session.flush()

        # -------------------------------------------------
        # Orders
        # -------------------------------------------------

        orders = [
            Order(
                id=45821,
                customer_id=customers[0].id,
                product="NovaPhone X1",
                amount=69999.00,
                status="Shipped",
                tracking_number="NVC45821001",
                order_date=datetime(2026, 9, 5, 10, 30),
                expected_delivery_date=date(2026, 9, 16),
            ),
            Order(
                id=45822,
                customer_id=customers[0].id,
                product="NovaBuds Pro",
                amount=8999.00,
                status="Processing",
                tracking_number=None,
                order_date=datetime(2026, 9, 10, 14, 15),
                expected_delivery_date=date(2026, 9, 17),
            ),
            Order(
                id=45823,
                customer_id=customers[1].id,
                product="NovaBook Air 14",
                amount=74999.00,
                status="Delivered",
                tracking_number="NVC45823001",
                order_date=datetime(2026, 8, 28, 9, 45),
                expected_delivery_date=date(2026, 9, 3),
            ),
            Order(
                id=45824,
                customer_id=customers[1].id,
                product="NovaWatch S2",
                amount=12999.00,
                status="Failed",
                tracking_number=None,
                order_date=datetime(2026, 9, 11, 11, 20),
                expected_delivery_date=None,
            ),
            Order(
                id=45825,
                customer_id=customers[2].id,
                product="NovaTab 11",
                amount=29999.00,
                status="Processing",
                tracking_number=None,
                order_date=datetime(2026, 9, 12, 16, 40),
                expected_delivery_date=date(2026, 9, 19),
            ),
            Order(
                id=45826,
                customer_id=customers[3].id,
                product="NovaCharge 65W",
                amount=2499.00,
                status="Cancelled",
                tracking_number=None,
                order_date=datetime(2026, 9, 6, 13, 10),
                expected_delivery_date=None,
            ),
        ]

        session.add_all(orders)
        session.flush()

        # -------------------------------------------------
        # Payments
        # -------------------------------------------------

        payments = [
            Payment(
                order_id=45821,
                amount=69999.00,
                status="Captured",
                payment_date=datetime(
                    2026, 9, 5, 10, 31
                ),
            ),
            Payment(
                order_id=45822,
                amount=8999.00,
                status="Captured",
                payment_date=datetime(
                    2026, 9, 10, 14, 16
                ),
            ),
            Payment(
                order_id=45823,
                amount=74999.00,
                status="Captured",
                payment_date=datetime(
                    2026, 8, 28, 9, 46
                ),
            ),
            Payment(
                order_id=45824,
                amount=12999.00,
                status="Captured",
                payment_date=datetime(
                    2026, 9, 11, 11, 21
                ),
            ),
            Payment(
                order_id=45825,
                amount=29999.00,
                status="Failed",
                payment_date=datetime(
                    2026, 9, 12, 16, 41
                ),
            ),
            Payment(
                order_id=45826,
                amount=2499.00,
                status="Refunded",
                payment_date=datetime(
                    2026, 9, 6, 13, 11
                ),
            ),
        ]

        session.add_all(payments)

        session.commit()

        print("NovaCart database seeded successfully.")
        print(f"Customers created: {len(customers)}")
        print(f"Orders created: {len(orders)}")
        print(f"Payments created: {len(payments)}")


if __name__ == "__main__":
    seed_database()