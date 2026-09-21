import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


from app.tools.support_tools import escalate_to_human


def main():
    print("\n" + "=" * 80)
    print("TESTING HUMAN ESCALATION")
    print("=" * 80)

    result = escalate_to_human.invoke(
        {
            "customer_id": 1,
            "reason": (
                "Customer reports that payment was deducted "
                "but order 45824 failed."
            ),
            "order_id": 45824,
            "priority": "high",
        }
    )

    print("\nEscalation result:")
    print(result)


if __name__ == "__main__":
    main()