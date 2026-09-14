from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

import sys

from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import Base
from app.database import models


def test_database_tables_exist(tmp_path):

    database_path = tmp_path / "test.db"

    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)

    tables = set(
        inspector.get_table_names()
    )

    expected_tables = {
        "customers",
        "orders",
        "payments",
        "tickets",
    }

    assert expected_tables.issubset(tables)


def test_customer_model_can_be_saved(tmp_path):

    database_path = tmp_path / "test_customer.db"

    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)

    with Session() as session:

        customer = models.Customer(
            name="Test Customer",
            email="test@example.com",
        )

        session.add(customer)
        session.commit()
        session.refresh(customer)

        assert customer.id is not None
        assert customer.name == "Test Customer"