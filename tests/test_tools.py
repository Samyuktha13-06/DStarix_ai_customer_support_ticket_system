import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.tools.order_tools import (
    check_order_status,
    get_delivery_status,
)
from app.tools.payment_tools import (
    check_payment_status,
)


def test_check_order_status_invalid_id():

    result = check_order_status.invoke(
        {"order_id": -1}
    )

    assert result["success"] is False


def test_check_payment_status_invalid_id():

    result = check_payment_status.invoke(
        {"order_id": 0}
    )

    assert result["success"] is False


def test_get_delivery_status_invalid_id():

    result = get_delivery_status.invoke(
        {"order_id": -100}
    )

    assert result["success"] is False