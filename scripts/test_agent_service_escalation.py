
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.services.agent_service import get_agent_service


def main():

    service = get_agent_service()

    print("\n" + "=" * 80)
    print("TESTING AGENT SERVICE ESCALATION")
    print("=" * 80)

    result = service.chat(
        message=(
            "I want to speak with a human support "
            "representative about order 45824."
        ),
        thread_id="agent-service-escalation-test",
    )

    print("\nANSWER:")
    print(result["answer"])

    print("\nESCALATED:")
    print(result["escalated"])

    print("\nTICKET ID:")
    print(result["ticket_id"])

    print("\n" + "=" * 80)

    assert result["escalated"] is True
    assert result["ticket_id"] is not None

    print("TEST PASSED")


if __name__ == "__main__":
    main()