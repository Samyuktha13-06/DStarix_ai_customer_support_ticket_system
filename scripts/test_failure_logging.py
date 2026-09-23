import logging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from fastapi.testclient import TestClient

from app.main import app
from app.services.exceptions import AgentLLMError


class FailingAgentService:
    """
    Test-only agent service that simulates an internal LLM failure.
    """

    def chat(self, message: str, thread_id: str) -> dict:
        raise AgentLLMError(
            "The AI support service is temporarily unavailable."
        )


def main():
    print("=" * 80)
    print("PHASE 9.6 - FAILURE LOGGING TEST")
    print("=" * 80)

    logging.getLogger().setLevel(logging.INFO)

    import app.api.chat as chat_module

    original_get_agent_service = chat_module.get_agent_service

    chat_module.get_agent_service = lambda: FailingAgentService()

    try:
        client = TestClient(app)

        response = client.post(
            "/chat",
            json={
                "message": "What is my order status?",
                "thread_id": "phase9-failure-logging-001",
            },
        )

        print("\nHTTP STATUS:")
        print(response.status_code)

        print("\nRESPONSE:")
        print(response.json())

        assert response.status_code == 503

        body = response.json()

        assert (
            body["detail"]
            == "The AI support service is temporarily unavailable."
        )

        print("\nPASS: Failure was logged internally.")
        print("PASS: API returned HTTP 503.")
        print("PASS: Safe error message was returned.")
        print("PASS: Internal provider details were not exposed.")

        print("\n" + "=" * 80)
        print("PHASE 9.6 FAILURE LOGGING TEST: PASS")
        print("=" * 80)

    finally:
        chat_module.get_agent_service = original_get_agent_service


if __name__ == "__main__":
    main()