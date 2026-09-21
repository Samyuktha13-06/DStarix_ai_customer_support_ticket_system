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

from app.tools.support_tools import (
    escalate_to_human,
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


def test_escalate_to_human_creates_ticket():
    result = escalate_to_human.invoke(
        {
            "customer_id": 1,
            "reason": "Customer requested human support.",
            "priority": "high",
        }
    )

    assert result["success"] is True
    assert result["escalated"] is True
    assert result["ticket_id"] is not None
    assert result["customer_id"] == 1
    assert result["priority"] == "high"
    assert result["status"] == "open"


def test_escalate_to_human_requires_reason():
    result = escalate_to_human.invoke(
        {
            "customer_id": 1,
            "reason": "",
        }
    )

    assert result["success"] is False
    assert "reason" in result["error"].lower()