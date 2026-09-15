from app.tools.order_tools import (
    check_order_status,
    get_delivery_status,
)

from app.tools.payment_tools import (
    check_payment_status,
)

from app.tools.support_tools import (
    create_support_ticket,
    escalate_to_human,
)


ALL_SUPPORT_TOOLS = [
    check_order_status,
    check_payment_status,
    get_delivery_status,
    create_support_ticket,
    escalate_to_human,
]