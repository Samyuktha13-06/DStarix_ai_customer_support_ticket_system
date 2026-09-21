import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


from app.services.agent_service import get_agent_service


def main():

    service = get_agent_service()

    print("\n" + "=" * 80)
    print("TESTING NORMAL AGENT RESPONSE")
    print("=" * 80)

    result = service.chat(
        message="How long does standard delivery take?",
        thread_id="agent-service-normal-test",
    )

    print("\nANSWER:")
    print(result["answer"])

    print("\nESCALATED:")
    print(result["escalated"])

    print("\nTICKET ID:")
    print(result["ticket_id"])

    assert result["escalated"] is False
    assert result["ticket_id"] is None

    print("\nTEST PASSED")


if __name__ == "__main__":
    main()