
import sys

from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from fastapi.testclient import TestClient

from app.main import app
from app.services.exceptions import AgentLLMError


class FailingAgentService:

    def chat(self, message: str, thread_id: str) -> dict:
        raise AgentLLMError(
            "The AI support service is temporarily unavailable."
        )


def main():
    import app.api.chat as chat_module

    original_get_agent_service = (
        chat_module.get_agent_service
    )

    chat_module.get_agent_service = (
        lambda: FailingAgentService()
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/chat",
            json={
                "message": "What is your refund policy?",
                "thread_id": "phase9-api-llm-failure-001",
            },
        )

        print("\n" + "=" * 80)
        print("PHASE 9.4 - API LLM FAILURE TEST")
        print("=" * 80)

        print("\nHTTP STATUS:")
        print(response.status_code)

        print("\nRESPONSE:")
        print(response.json())

        assert response.status_code == 503

        assert response.json()["detail"] == (
            "The AI support service is temporarily unavailable."
        )

        print("\nPASS: API returned HTTP 503.")

        print(
            "PASS: Safe LLM failure message returned."
        )

        print(
            "PASS: Internal provider error was not exposed."
        )

        print("\n" + "=" * 80)
        print("PHASE 9.4 API TEST: PASS")
        print("=" * 80)

    finally:
        # Restore the original dependency/function.
        chat_module.get_agent_service = (
            original_get_agent_service
        )


if __name__ == "__main__":
    main()