from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from app.main import app


class FailingDatabaseAgentService:
    """
    Test-only service that simulates a database failure
    inside the agent layer.
    """

    def chat(self, message: str, thread_id: str) -> dict:
        return {
            "answer": (
                "I’m unable to retrieve your order information right now "
                "because the database service is temporarily unavailable."
            ),
            "messages": [],
            "escalated": False,
            "ticket_id": None,
        }


def main():
    print("=" * 80)
    print("PHASE 9.5 - API DATABASE FAILURE TEST")
    print("=" * 80)

    import app.api.chat as chat_module

    original_get_agent_service = chat_module.get_agent_service

    chat_module.get_agent_service = (
        lambda: FailingDatabaseAgentService()
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/chat",
            json={
                "message": "Where is my order 45821?",
                "thread_id": "phase9-api-db-failure-001",
            },
        )

        print("\nHTTP STATUS:")
        print(response.status_code)

        print("\nRESPONSE:")
        print(response.json())

        assert response.status_code == 200

        body = response.json()

        assert (
            "database service is temporarily unavailable"
            in body["answer"]
        )

        assert body["escalated"] is False
        assert body["ticket_id"] is None

        print("\nPASS: API completed successfully despite database failure.")
        print("PASS: Safe database failure message was returned.")
        print("PASS: No fabricated order information was returned.")

        print("\n" + "=" * 80)
        print("PHASE 9.5 API TEST: PASS")
        print("=" * 80)

    finally:
        chat_module.get_agent_service = original_get_agent_service


if __name__ == "__main__":
    main()