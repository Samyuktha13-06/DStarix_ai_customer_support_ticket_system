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
    create_support_ticket,escalate_to_human
)

from app.tools.rag_tools import (
    search_knowledge_base,
)


def main() -> None:

    print("\nORDER STATUS")
    print("=" * 60)

    result = check_order_status.invoke(
        {"order_id": 45821}
    )

    print(result)

    print("\nDELIVERY STATUS")
    print("=" * 60)

    result = get_delivery_status.invoke(
        {"order_id": 45821}
    )

    print(result)

    print("\nPAYMENT STATUS")
    print("=" * 60)

    result = check_payment_status.invoke(
        {"order_id": 45821}
    )

    print(result)


    print("\nFAILED ORDER + CAPTURED PAYMENT")
    print("=" * 60)

    order_result = check_order_status.invoke(
        {"order_id": 45824}
    )

    payment_result = check_payment_status.invoke(
        {"order_id": 45824}
    )

    print("ORDER:")
    print(order_result)

    print("\nPAYMENT:")
    print(payment_result)



    print("\nCREATE TICKET")
    print("=" * 60)

    ticket_result = create_support_ticket.invoke(
        {
            "customer_id": 2,
            "subject": "Payment captured for failed order",
            "description": (
                "Order 45824 failed, but the payment "
                "was captured and requires investigation."
            ),
            "priority": "high",
            "order_id": 45824,
        }
    )

    print(ticket_result)



    print("\nHUMAN ESCALATION")
    print("=" * 60)

    escalation_result = escalate_to_human.invoke(
        {
            "customer_id": 2,
            "reason": (
                "Customer reports that payment was deducted "
                "even though order 45824 failed."
            ),
            "order_id": 45824,
            "priority": "urgent",
        }
    )

    print(escalation_result)



    print("\nKNOWLEDGE BASE SEARCH")
    print("=" * 60)

    result = search_knowledge_base.invoke(
        {
            "query": "What is the refund policy?"
        }
    )

    print(result)

if __name__ == "__main__":
    main()