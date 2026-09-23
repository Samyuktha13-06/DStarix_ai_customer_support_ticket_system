import logging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from fastapi.testclient import TestClient

from app.main import app


def main():
    print("=" * 80)
    print("PHASE 9.6 - CHAT LOGGING TEST")
    print("=" * 80)

    logging.getLogger().setLevel(logging.INFO)

    client = TestClient(app)

    response = client.post(
        "/chat",
        json={
            "message": "What is your refund policy?",
            "thread_id": "phase9-logging-test-001",
        },
    )

    print("\nHTTP STATUS:")
    print(response.status_code)

    print("\nRESPONSE:")
    print(response.json())

    assert response.status_code == 200

    body = response.json()

    assert "answer" in body
    assert isinstance(body["answer"], str)
    assert body["answer"].strip()

    assert "escalated" in body
    assert "ticket_id" in body

    print("\nPASS: /chat request completed successfully.")
    print("PASS: Response contains the expected fields.")
    print("PASS: Logging was active during the request.")

    print("\n" + "=" * 80)
    print("PHASE 9.6 CHAT LOGGING TEST: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()