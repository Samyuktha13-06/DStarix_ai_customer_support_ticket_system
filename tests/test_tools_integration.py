import pytest

from app.tools.order_tools import (
    check_order_status,
    get_delivery_status,
)
from app.tools.payment_tools import (
    check_payment_status,
)


@pytest.mark.integration
def test_order_tool_returns_real_order():

    result = check_order_status.invoke(
        {"order_id": 45821}
    )

    assert result["success"] is True
    assert result["order"]["order_id"] == 45821
    assert result["order"]["status"] == "Shipped"


@pytest.mark.integration
def test_delivery_tool_returns_tracking():

    result = get_delivery_status.invoke(
        {"order_id": 45821}
    )

    assert result["success"] is True
    assert (
        result["delivery"]["tracking_number"]
        == "NVC45821001"
    )


@pytest.mark.integration
def test_payment_tool_returns_payment():

    result = check_payment_status.invoke(
        {"order_id": 45824}
    )

    assert result["success"] is True
    assert (
        result["payment"]["status"]
        == "Captured"
    )