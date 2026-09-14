from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.database.database import Base
from app.database.models import (
    Customer,
    Order,
    Payment,
)


def create_test_database(tmp_path):

    database_path = tmp_path / "seed_test.db"

    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    return engine


def test_seed_data_relationships(tmp_path):

    engine = create_test_database(tmp_path)

    Session = sessionmaker(bind=engine)

    with Session() as session:

        customer = Customer(
            name="Test Customer",
            email="seed@example.com",
        )

        session.add(customer)
        session.flush()

        order = Order(
            id=45821,
            customer_id=customer.id,
            product="NovaPhone X1",
            amount=69999.00,
            status="Shipped",
            tracking_number="NVC45821001",
        )

        session.add(order)
        session.flush()

        payment = Payment(
            order_id=order.id,
            amount=69999.00,
            status="Captured",
        )

        session.add(payment)
        session.commit()

        stored_order = session.scalar(
            select(Order).where(
                Order.id == 45821
            )
        )

        stored_payment = session.scalar(
            select(Payment).where(
                Payment.order_id == 45821
            )
        )

        assert stored_order is not None
        assert stored_order.customer_id == customer.id
        assert stored_order.status == "Shipped"

        assert stored_payment is not None
        assert stored_payment.status == "Captured"